from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os, shutil, uuid
from database import get_db, init_db

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("/app/data", exist_ok=True)

app = FastAPI(title="PDF CMS")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def startup():
    init_db()

# ── Serve frontend ──────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ── CREATE ──────────────────────────────────────────────────────────────────
@app.post("/documents")
async def upload_document(
    title: str = Form(...),
    description: str = Form(""),
    tags: str = Form(""),
    file: UploadFile = File(...)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    unique_name = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    file_size = len(content)
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os, shutil, uuid
from database import get_db, init_db

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("/app/data", exist_ok=True)

app = FastAPI(title="PDF CMS")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def startup():
    init_db()

# ── Serve frontend ──────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ── CREATE ──────────────────────────────────────────────────────────────────
@app.post("/documents")
async def upload_document(
    title: str = Form(...),
    description: str = Form(""),
    tags: str = Form(""),
    file: UploadFile = File(...)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    unique_name = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    file_size = 0
    with open(file_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):  
            f.write(chunk)
            file_size += len(chunk)

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO documents (title, description, tags, filename, original_name, file_size) VALUES (?,?,?,?,?,?)",
        (title, description, tags, unique_name, file.filename, file_size)
    )
    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()

    return {"id": doc_id, "message": "Document uploaded successfully."}

# ── READ ALL ────────────────────────────────────────────────────────────────
@app.get("/documents")
def list_documents(search: str = ""):
    conn = get_db()
    if search:
        rows = conn.execute(
            "SELECT * FROM documents WHERE title LIKE ? OR tags LIKE ? OR description LIKE ? ORDER BY created_at DESC",
            (f"%{search}%", f"%{search}%", f"%{search}%")
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── READ ONE ────────────────────────────────────────────────────────────────
@app.get("/documents/{doc_id}")
def get_document(doc_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found.")
    return dict(row)

# ── DOWNLOAD ────────────────────────────────────────────────────────────────
@app.get("/documents/{doc_id}/file")
def download_document(doc_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found.")
    file_path = os.path.join(UPLOAD_DIR, row["filename"])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File missing from storage.")
    return FileResponse(file_path, media_type="application/pdf", filename=row["original_name"])

# ── UPDATE ──────────────────────────────────────────────────────────────────
@app.put("/documents/{doc_id}")
def update_document(doc_id: int, title: str = Form(...), description: str = Form(""), tags: str = Form("")):
    conn = get_db()
    row = conn.execute("SELECT id FROM documents WHERE id=?", (doc_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found.")
    conn.execute(
        "UPDATE documents SET title=?, description=?, tags=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (title, description, tags, doc_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Document updated successfully."}

# ── DELETE ──────────────────────────────────────────────────────────────────
@app.delete("/documents/{doc_id}")
def delete_document(doc_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found.")
    file_path = os.path.join(UPLOAD_DIR, row["filename"])
    if os.path.exists(file_path):
        os.remove(file_path)
    conn.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()
    return {"message": "Document deleted successfully."}
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO documents (title, description, tags, filename, original_name, file_size) VALUES (?,?,?,?,?,?)",
        (title, description, tags, unique_name, file.filename, file_size)
    )
    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()

    return {"id": doc_id, "message": "Document uploaded successfully."}

# ── READ ALL ────────────────────────────────────────────────────────────────
@app.get("/documents")
def list_documents(search: str = ""):
    conn = get_db()
    if search:
        rows = conn.execute(
            "SELECT * FROM documents WHERE title LIKE ? OR tags LIKE ? OR description LIKE ? ORDER BY created_at DESC",
            (f"%{search}%", f"%{search}%", f"%{search}%")
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── READ ONE ────────────────────────────────────────────────────────────────
@app.get("/documents/{doc_id}")
def get_document(doc_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found.")
    return dict(row)

# ── DOWNLOAD ────────────────────────────────────────────────────────────────
@app.get("/documents/{doc_id}/file")
def download_document(doc_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found.")
    file_path = os.path.join(UPLOAD_DIR, row["filename"])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File missing from storage.")
    return FileResponse(file_path, media_type="application/pdf", filename=row["original_name"])

# ── UPDATE ──────────────────────────────────────────────────────────────────
@app.put("/documents/{doc_id}")
def update_document(doc_id: int, title: str = Form(...), description: str = Form(""), tags: str = Form("")):
    conn = get_db()
    row = conn.execute("SELECT id FROM documents WHERE id=?", (doc_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found.")
    conn.execute(
        "UPDATE documents SET title=?, description=?, tags=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (title, description, tags, doc_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Document updated successfully."}

# ── DELETE ──────────────────────────────────────────────────────────────────
@app.delete("/documents/{doc_id}")
def delete_document(doc_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found.")
    file_path = os.path.join(UPLOAD_DIR, row["filename"])
    if os.path.exists(file_path):
        os.remove(file_path)
    conn.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()
    return {"message": "Document deleted successfully."}

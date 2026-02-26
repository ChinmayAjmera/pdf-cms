"""
seed.py — Runs once on startup.
Checks if the DB is empty, and if so, copies demo PDFs into /app/uploads
and inserts their metadata into SQLite.
"""

import os
import shutil
from database import get_db, init_db

DEMO_DIR = "/app/demo-files"
UPLOAD_DIR = "/app/uploads"

DEMO_DOCS = [
    {
        "filename": "DSA-revision-guide.pdf",
        "title": "DSA Guide",
        "description": "Guide for data structures and algorithms, perfect for interview prep.",
        "tags": "dsa, guide, interview, prep",
    },
    {
        "filename": "The Cloud Resume Challenge Cookbook (AWS Edition) -- Forrest Brazeal.pdf",
        "title": "The Cloud Resume Challenge Cookbook (AWS Edition) -- Forrest Brazeal",
        "description": "Comprehensive guide to building and deploying a resume website on AWS, with step-by-step instructions and best practices.",
        "tags": "cloud, aws, misc",
    },
    {
        "filename": "Efficient Linux at the Command Line (2022, O'Reilly Media) - Daniel J Barrett.pdf",
        "title": "Efficient Linux at the Command Line (2022, O'Reilly Media) - Daniel J Barrett",
        "description": "Practical guide to mastering Linux command line tools and techniques for efficient system administration and development.",
        "tags": "linux, textbook, system-administration, O'Reilly",
    },
]

def seed():
    init_db()
    conn = get_db()

    # Only seed if the table is empty
    count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    if count > 0:
        print(f"[seed] DB already has {count} document(s). Skipping seed.")
        conn.close()
        return

    print("[seed] Empty DB detected. Seeding demo documents...")

    for doc in DEMO_DOCS:
        src = os.path.join(DEMO_DIR, doc["filename"])
        if not os.path.exists(src):
            print(f"[seed] Warning: {src} not found, skipping.")
            continue

        # Copy to uploads with original filename (demo files keep their name)
        dst = os.path.join(UPLOAD_DIR, doc["filename"])
        shutil.copy2(src, dst)

        file_size = os.path.getsize(dst)

        conn.execute(
            "INSERT INTO documents (title, description, tags, filename, original_name, file_size) VALUES (?,?,?,?,?,?)",
            (doc["title"], doc["description"], doc["tags"], doc["filename"], doc["filename"], file_size)
        )
        print(f"[seed] Added: {doc['title']}")

    conn.commit()
    conn.close()
    print("[seed] Done.")

if __name__ == "__main__":
    seed()

# main.py
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List
from fastapi.templating import Jinja2Templates

app = FastAPI()
tpl = Jinja2Templates("templates")

class Post(BaseModel):
    id: int
    title: str
    content: str

@app.get("/")
async def index(r: Request):
    return tpl.TemplateResponse("index.html", {"request": r})

def init_db():
    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/posts", response_model=List[Post])
def get_posts():
    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content FROM posts")
    rows = cursor.fetchall()
    conn.close()
    return [Post(id=row[0], title=row[1], content=row[2]) for row in rows]

@app.post("/posts", response_model=Post)
def create_post(post: Post):
    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO posts (id, title, content) VALUES (?, ?, ?)", (post.id, post.title, post.content))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="El ID ya existe")
    finally:
        conn.close()
    return post

@app.get("/posts/{post_id}", response_model=Post)
def get_post(post_id: int):
    conn = sqlite3.connect("blog.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content FROM posts WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Post(id=row[0], title=row[1], content=row[2])
    else:
        raise HTTPException(status_code=404, detail="Post no encontrado")

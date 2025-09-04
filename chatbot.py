# File: chatbot_with_db.py

import os
import sqlite3
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("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")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY not found in environment. Please set it in a .env file.")

client = OpenAI(api_key=api_key)

# Database setup
DB_FILE = "chatbot.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def get_or_create_user(username: str, email: str = None):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    if row:
        user_id = row[0]
    else:
        cur.execute("INSERT INTO users (username, email) VALUES (?, ?)", (username, email))
        conn.commit()
        user_id = cur.lastrowid
    conn.close()
    return user_id

def save_message(user_id: int, role: str, content: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chats (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, role, content, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def load_chat_history(user_id: int, limit: int = 20):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT role, content FROM chats WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cur.fetchall()
    conn.close()
    return [{"role": role, "content": content} for role, content in reversed(rows)]

def chat_with_gpt(user_id: int):
    print("Chatbot ready! Type 'exit' to quit.\n")
    
    conversation = [{"role": "system", "content": "You are a helpful assistant."}]
    conversation.extend(load_chat_history(user_id))

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        conversation.append({"role": "user", "content": user_input})
        save_message(user_id, "user", user_input)

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation,
                max_tokens=500
            )

            reply = response.choices[0].message.content.strip()
            print(f"Bot: {reply}\n")

            conversation.append({"role": "assistant", "content": reply})
            save_message(user_id, "assistant", reply)

            if len(conversation) > 25:
                conversation = conversation[:1] + conversation[-24:]

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    init_db()
    username = input("Enter your username: ").strip()
    email = input("Enter your email (optional): ").strip() or None
    user_id = get_or_create_user(username, email)
    chat_with_gpt(user_id)

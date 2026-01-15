import sqlite3
from datetime import datetime
from app.models import get_connection

def insert_message(data):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["message_id"],
            data["from"],
            data["to"],
            data["ts"],
            data.get("text"),
            datetime.utcnow().isoformat() + "Z"
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

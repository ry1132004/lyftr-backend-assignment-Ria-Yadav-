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

def list_messages(limit, offset):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT message_id, from_msisdn, to_msisdn, ts, text
    FROM messages
    ORDER BY ts ASC, message_id ASC
    LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM messages")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT from_msisdn) FROM messages")
    senders = cursor.fetchone()[0]

    cursor.execute("""
    SELECT from_msisdn, COUNT(*) 
    FROM messages 
    GROUP BY from_msisdn 
    ORDER BY COUNT(*) DESC 
    LIMIT 10
    """)
    per_sender = [{"from": r[0], "count": r[1]} for r in cursor.fetchall()]

    cursor.execute("SELECT MIN(ts), MAX(ts) FROM messages")
    first, last = cursor.fetchone()

    conn.close()

    return {
        "total_messages": total,
        "senders_count": senders,
        "messages_per_sender": per_sender,
        "first_message_ts": first,
        "last_message_ts": last
    }

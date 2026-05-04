from flask import Flask, render_template, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB = "analytics.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            date TEXT,
            time TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_visit(ip):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    c.execute("INSERT INTO visits (ip, date, time) VALUES (?, ?, ?)",
              (ip, date, time))

    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM visits")
    total = c.fetchone()[0]

    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(DISTINCT ip) FROM visits WHERE date = ?", (today,))
    dau = c.fetchone()[0]

    conn.close()
    return total, dau


@app.route("/")
def home():
    init_db()
    ip = request.remote_addr
    log_visit(ip)

    # ❌ NOT sent to HTML anymore
    return render_template("index.html")


# 🔐 PRIVATE ADMIN ONLY (you)
@app.route("/admin")
def admin():
    total, dau = get_stats()

    return f"""
    <h2>Private Analytics Dashboard</h2>
    <p>Total visits: {total}</p>
    <p>Daily Active Users: {dau}</p>
    """
    

if __name__ == "__main__":
    app.run(debug=True)
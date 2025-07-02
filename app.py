from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# Ensure database and table exist
DB_FILE = "music.db"
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            artist TEXT,
            image TEXT,
            rating_sum INTEGER DEFAULT 0,
            rating_count INTEGER DEFAULT 0
        )
        """)
        # Insert sample songs if not already present
        c.execute("SELECT COUNT(*) FROM songs")
        if c.fetchone()[0] == 0:
            songs = [
                ("Mandla’s Vibe", "DJ Mandia", "song1.jpg"),
                ("Ngiyakutsandza", "Sindy & The Beats", "song2.jpg"),
                ("Buhle Bakho", "Thando Fresh", "song3.jpg"),
                ("Emadloti", "Mkhulu N’ Sons", "song4.jpg"),
                ("Kwentekani?", "Vibe Nation", "song5.jpg"),
            ]
            c.executemany("INSERT INTO songs (title, artist, image) VALUES (?, ?, ?)", songs)
        conn.commit()

@app.route("/")
def home():
    return redirect("/hitlist")

@app.route("/hitlist")
def hitlist():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
        SELECT title, artist, image, rating_sum, rating_count,
               CASE WHEN rating_count > 0 THEN ROUND(rating_sum * 1.0 / rating_count, 2)
                    ELSE 0 END AS average_rating
        FROM songs
        ORDER BY average_rating DESC
        LIMIT 5
        """)
        top_songs = c.fetchall()
    return render_template("hitlist.html", songs=top_songs)

@app.route("/rate", methods=["GET", "POST"])
def rate():
    if request.method == "POST":
        title = request.form.get("song")
        rating = int(request.form.get("rating"))

        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("UPDATE songs SET rating_sum = rating_sum + ?, rating_count = rating_count + 1 WHERE title = ?", (rating, title))
            conn.commit()
        return redirect("/hitlist")
    else:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT title FROM songs")
            all_titles = [row[0] for row in c.fetchall()]
        return render_template("rate.html", songs=all_titles)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
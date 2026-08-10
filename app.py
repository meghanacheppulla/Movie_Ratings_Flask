import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "movies.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-before-real-deployment")

MOVIES = ["Bahubali", "salaar", "RRR","pushpa"]


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )"""
    )
    db.execute(
        """CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )"""
    )
    db.execute(
        """CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            vote TEXT CHECK(vote IN ('like', 'dislike')) NOT NULL,
            UNIQUE(user_id, movie_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(movie_id) REFERENCES movies(id)
        )"""
    )
    for name in MOVIES:
        db.execute("INSERT OR IGNORE INTO movies (name) VALUES (?)", (name,))
    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("movies_page"))
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not username or not password:
            flash("Please fill in both fields.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        else:
            db = get_db()
            existing = db.execute(
                "SELECT id FROM users WHERE username = ?", (username,)
            ).fetchone()
            if existing:
                flash("That username is already taken.", "error")
            else:
                db.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
                flash("Account created! Please log in.", "success")
                return redirect(url_for("login"))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("movies_page"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Movies + voting
# ---------------------------------------------------------------------------
def login_required(view):
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    wrapped.__name__ = view.__name__
    return wrapped


@app.route("/movies")
@login_required
def movies_page():
    db = get_db()
    movies = db.execute("SELECT * FROM movies ORDER BY id").fetchall()

    my_votes = {
        row["movie_id"]: row["vote"]
        for row in db.execute(
            "SELECT movie_id, vote FROM votes WHERE user_id = ?",
            (session["user_id"],),
        ).fetchall()
    }

    tally = []
    for m in movies:
        likes = db.execute(
            "SELECT COUNT(*) AS c FROM votes WHERE movie_id = ? AND vote = 'like'",
            (m["id"],),
        ).fetchone()["c"]
        dislikes = db.execute(
            "SELECT COUNT(*) AS c FROM votes WHERE movie_id = ? AND vote = 'dislike'",
            (m["id"],),
        ).fetchone()["c"]
        tally.append({"name": m["name"], "likes": likes, "dislikes": dislikes})

    return render_template(
        "movies.html",
        movies=movies,
        my_votes=my_votes,
        tally=tally,
        username=session.get("username"),
    )


@app.route("/vote", methods=["POST"])
@login_required
def vote():
    db = get_db()
    movies = db.execute("SELECT * FROM movies ORDER BY id").fetchall()

    for m in movies:
        choice = request.form.get(f"movie_{m['id']}")
        if choice in ("like", "dislike"):
            db.execute(
                """INSERT INTO votes (user_id, movie_id, vote)
                   VALUES (?, ?, ?)
                   ON CONFLICT(user_id, movie_id)
                   DO UPDATE SET vote = excluded.vote""",
                (session["user_id"], m["id"], choice),
            )
    db.commit()
    flash("Your ratings have been submitted!", "success")
    return redirect(url_for("movies_page"))


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)

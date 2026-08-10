# Reel Votes — Movie Rating App

A small Flask web app matching your wireframe:

1. **Login / Sign up** page
2. **Movies** page — three movies, each with a 👍 Like / 👎 Dislike choice
3. After you submit, a **live tally table** below shows Positive / Negative counts per movie

Accounts and votes are stored in a local SQLite file (`movies.db`), created
automatically the first time you run the app. Each user can vote once per
movie — voting again updates their previous choice instead of double-counting.

## 1. Install and run

You need Python 3.9+ installed. Then, in this folder:

```bash
pip install -r requirements.txt
python app.py
```

You'll see output like:

```
* Running on http://127.0.0.1:5000
* Running on http://192.168.1.23:5000   <-- your machine's local IP
```

Open **http://127.0.0.1:5000** in your own browser to try it.

## 2. Give your friend a link

The app already runs with `host="0.0.0.0"`, which means it accepts
connections from other devices — not just your own laptop. Which option
below works depends on whether your friend is on the same network as you.

### Option A — Same Wi‑Fi / network (easiest, free)

1. Find your laptop's local IP address:
   - **Windows:** open Command Prompt → `ipconfig` → look for "IPv4 Address"
   - **Mac/Linux:** open Terminal → `ifconfig` or `ip a` → look for something
     like `192.168.x.x`
2. Make sure your firewall allows incoming connections on port 5000.
3. Share this with your friend: `http://<your-ip>:5000` (e.g.
   `http://192.168.1.23:5000`).
4. Your friend must be connected to the **same Wi‑Fi/router** as you, and
   your laptop + `python app.py` need to stay running while they use it.

### Option B — Different networks (friend is elsewhere)

Your laptop isn't reachable from the public internet by default, so you need
a tunnel or a host. Two easy, free ways:

- **ngrok** (quick, temporary link):
  1. Install from https://ngrok.com/download and sign up for a free account.
  2. Run your Flask app (`python app.py`) in one terminal.
  3. In another terminal: `ngrok http 5000`
  4. ngrok prints a public URL like `https://abc123.ngrok-free.app` — send
     that to your friend. It works as long as both `python app.py` and
     `ngrok` keep running on your laptop.

- **Free hosting** (permanent link, app runs even when your laptop is off):
  Deploy this folder to a free-tier host such as **Render**, **Railway**, or
  **PythonAnywhere**. They all support Flask apps directly — you push this
  code, they give you a permanent `https://yourapp.onrender.com`-style URL.
  This is the better option if you want the link to keep working long-term.

> Note: `debug=True` in `app.py` is convenient for development but should be
> turned off (`debug=False`) before sharing the app with anyone, since debug
> mode exposes an interactive code debugger if something crashes.

## 3. Project structure

```
movie_rating_app/
├── app.py                 # Flask routes, auth, voting logic, SQLite setup
├── requirements.txt
├── templates/
│   ├── base.html          # shared layout, nav, flash messages
│   ├── login.html
│   ├── signup.html
│   └── movies.html        # movie cards + live results table
└── static/
    └── style.css           # marquee / cinema-themed styling
```

## 4. Changing the movies

Edit the `MOVIES` list near the top of `app.py`, then delete `movies.db` (or
just add new rows) so the new titles get seeded in.

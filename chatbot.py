from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret")

USERS_FILE = "users.json"

# --- Simple chatbot stub ---
def respond_to(message, username=None):
    # Replace this stub with your existing chatbot logic.
    # If your current chatbot.py already has a function to respond,
    # import and call that instead.
    return {"reply": f"You said: {message}"}

# --- User storage helpers ---
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def get_user(username):
    users = load_users()
    return users.get(username)

# --- Routes ---
@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("chat"))
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Username and password are required.", "warning")
            return redirect(url_for("signup"))

        users = load_users()
        if username in users:
            flash("Username already exists.", "danger")
            return redirect(url_for("signup"))

        users[username] = {
            "password_hash": generate_password_hash(password)
        }
        save_users(users)
        flash("Signup successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_user(username)
        if not user or not check_password_hash(user.get("password_hash", ""), password):
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))
        session["username"] = username
        flash("Logged in successfully.", "success")
        return redirect(url_for("chat"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/chat")
@login_required
def chat():
    return render_template("chat.html", username=session.get("username"))

@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json() or {}
    message = data.get("message", "")
    username = session.get("username")
    if not message:
        return jsonify({"error": "No message provided."}), 400
    result = respond_to(message, username=username)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

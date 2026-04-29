from flask import Flask, request, redirect
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return "tracker alive"

@app.route("/base")
def track():
    user_id = request.args.get("u")
    base_id = request.args.get("b")

    print("CLICK:", user_id, base_id, datetime.utcnow(), flush=True)

    return redirect(
        f"https://link.clashofclans.com/en?action=OpenLayout&id={base_id}"
    )
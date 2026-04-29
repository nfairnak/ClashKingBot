from flask import Flask, request, redirect
from datetime import datetime

print("TRACKER STARTING...")

app = Flask(__name__)

@app.route("/base")
def track():
    user_id = request.args.get("u")
    base_id = request.args.get("b")

    print("CLICK:", user_id, base_id, datetime.utcnow())

    return redirect(
        f"https://link.clashofclans.com/en?action=OpenLayout&id={base_id}"
    )

if __name__ == "__main__":
    print("RUNNING SERVER...")
    app.run(host="127.0.0.1", port=3000, debug=True)
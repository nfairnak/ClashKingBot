from flask import Flask, request, redirect
from datetime import datetime
import os
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
    app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 3000))
)
import os

if __name__ == "__main__":
    print("RUNNING SERVER...")
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 3000))
    )
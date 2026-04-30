from flask import Flask, request, redirect
from datetime import datetime
import requests
import pytz
import os

app = Flask(__name__)

# In-memory click counter.
# This resets whenever the app restarts.
base_clicks = {}


@app.route("/")
def home():
    return "tracker alive"


@app.route("/base")
def track():
    user_id = request.args.get("u")
    base_id = request.args.get("b")

    if not user_id or not base_id:
        return "Missing user ID or base ID", 400

    # Convert UTC to Eastern time
    utc_time = datetime.utcnow()
    eastern = pytz.timezone("US/Eastern")
    eastern_time = utc_time.replace(tzinfo=pytz.utc).astimezone(eastern)

    day = eastern_time.strftime("%A")
    time_str = eastern_time.strftime("%I:%M %p")

    # Update click count
    base_clicks[base_id] = base_clicks.get(base_id, 0) + 1
    click_count = base_clicks[base_id]

    # Format Discord log message
    log_message = (
        f"📅 **Date:** {day}, {time_str} EST\n"
        f"👤 **User:** <@{user_id}>\n"
        f"🏰 **Base:** `{base_id}`\n"
        f"📊 **Clicks:** {click_count}"
    )

    print(
        f"CLICK: User {user_id} clicked base {base_id} at {utc_time}",
        flush=True
    )

    # Send click log to your CloudWatch/click-log Discord webhook
    webhook_url = os.getenv("CLOUDWATCH_WEBHOOK_URL")

    if webhook_url:
        try:
            response = requests.post(
                webhook_url,
                json={"content": log_message},
                timeout=5
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Webhook failed: {e}", flush=True)
    else:
        print("CLOUDWATCH_WEBHOOK_URL is not set", flush=True)

    # Redirect user to Clash
    return redirect(
        f"https://link.clashofclans.com/en?action=OpenLayout&id={base_id}"
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000))
    )
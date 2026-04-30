from flask import Flask, request, redirect
from datetime import datetime
import requests
import pytz

app = Flask(__name__)

# In-memory click counter (resets on restart; for persistence, use a DB)
base_clicks = {}

@app.route("/")
def home():
    return "tracker alive"

@app.route("/base")
def track():
    user_id = request.args.get("u")
    base_id = request.args.get("b")

    # Convert UTC to EST
    utc_time = datetime.utcnow()
    est = pytz.timezone('US/Eastern')
    est_time = utc_time.replace(tzinfo=pytz.utc).astimezone(est)
    day = est_time.strftime('%A')  # e.g., Monday
    time_str = est_time.strftime('%I:%M %p')  # e.g., 06:30 PM

    # Update click count
    base_clicks[base_id] = base_clicks.get(base_id, 0) + 1
    click_count = base_clicks[base_id]

    # Format log message
    log_message = f"📅 **Date:** {day}, {time_str} EST\n👤 **User:** <@{user_id}>\n📊 **Clicks:** {click_count}"

    print(f"CLICK: User {user_id} clicked base {base_id} at {utc_time}", flush=True)

    # Send to Discord webhook
    webhook_url = "YOUR_WEBHOOK_URL"  # Replace with your actual Discord webhook URL
    data = {"content": log_message}
    requests.post(webhook_url, json=data)

    return redirect(
        f"https://link.clashofclans.com/en?action=OpenLayout&id={base_id}"
    )
    timestamp = datetime.utcnow()
    log_message = f"CLICK: User {user_id} clicked base {base_id} at {timestamp}"

    print(log_message, flush=True)

    # Send to Discord webhook
    webhook_url = "https://discord.com/api/webhooks/1499543197355872367/LIBUzDB-CvfMpu0Ej5igtNmpK3CDr-6BHz5BGSPntH7TZMaGac6_58xFzTccNkko-Xbw"  # Replace with your actual Discord webhook URL
    data = {"content": log_message}
    requests.post(webhook_url, json=data)

    return redirect(
        f"https://link.clashofclans.com/en?action=OpenLayout&id={base_id}"
    )
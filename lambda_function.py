import os
import requests
from datetime import datetime, timedelta
import pytz

def build_activesg_link():
    # Read environment variables (configurable in AWS Lambda)
    activity_id = os.environ["ACTIVITY_ID"]
    venue_id = os.environ["VENUE_ID"]

    # Set timezone to Singapore
    singapore_tz = pytz.timezone("Asia/Singapore")
    now = datetime.now(singapore_tz)

    # Determine target date (2 weeks later, same day)
    target_date = now + timedelta(weeks=2)
    date_str = target_date.strftime("%Y-%m-%d")

    # Define the 3pm and 4pm times (Singapore local time)
    slot_3pm = singapore_tz.localize(datetime(target_date.year, target_date.month, target_date.day, 15, 0))
    slot_4pm = singapore_tz.localize(datetime(target_date.year, target_date.month, target_date.day, 16, 0))

    # Convert to UNIX timestamps in milliseconds
    slot_3pm_ms = int(slot_3pm.timestamp() * 1000)
    slot_4pm_ms = int(slot_4pm.timestamp() * 1000)

    # Construct link
    link = (
        f"https://activesg.gov.sg/facility-bookings/activities/{activity_id}/venues/{venue_id}/timeslots"
        f"?date={date_str}&timeslots={slot_3pm_ms}&timeslots={slot_4pm_ms}"
    )

    return link


def send_telegram_message(message):
    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

    response = requests.post(url, data=payload)
    response.raise_for_status()


def lambda_handler(event, context):
    singapore_tz = pytz.timezone("Asia/Singapore")
    now = datetime.now(singapore_tz)
    weekday = now.strftime("%A")

    # Only send on Saturday or Sunday
    if weekday not in ["Saturday", "Sunday"]:
        return {"statusCode": 200, "body": "Not weekend. No message sent."}

    # Build ActiveSG link and message
    link = build_activesg_link()
    message = f"Please ballot, ignore if already have court for that week\n{link}"

    # Send message
    send_telegram_message(message)
    return {"statusCode": 200, "body": "Message sent successfully."}


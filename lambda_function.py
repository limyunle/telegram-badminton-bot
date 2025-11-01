import os
import requests
import datetime

# --- Configuration from environment variables ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
ACTIVITY_ID = os.environ.get("ACTIVITY_ID")
VENUE_ID = os.environ.get("VENUE_ID")

# Base URL template
BASE_URL_TEMPLATE = (
    "https://activesg.gov.sg/facility-bookings/activities/{activity}/venues/{venue}/timeslots"
)

# --- Helper Functions ---

def get_singapore_date():
    """Return the current date in Singapore timezone (UTC+8)."""
    sg_tz = datetime.timezone(datetime.timedelta(hours=8))
    return datetime.datetime.now(sg_tz).date()


def build_activesg_link(target_date: datetime.date):
    """Build ActiveSG booking URL for 3PM and 4PM timeslots."""
    tz_offset = datetime.timedelta(hours=8)

    def to_millis(hour: int):
        dt = datetime.datetime.combine(target_date, datetime.time(hour, 0)) + tz_offset
        return int(dt.timestamp() * 1000)

    timeslot_3pm = to_millis(15)
    timeslot_4pm = to_millis(16)

    base_url = BASE_URL_TEMPLATE.format(activity=ACTIVITY_ID, venue=VENUE_ID)
    url = (
        f"{base_url}?date={target_date.isoformat()}"
        f"&timeslots={timeslot_3pm}&timeslots={timeslot_4pm}"
    )
    return url


def send_telegram_message(message: str):
    """Send a message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Telegram message sent successfully.")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
        if 'response' in locals():
            print(response.text)


def lambda_handler(event=None, context=None):
    """
    Lambda entry point — runs every Saturday/Sunday 12PM SGT.
    Sends ActiveSG ballot link for the same day two weeks later.
    """
    today_sg = get_singapore_date()
    target_date = today_sg + datetime.timedelta(days=14)

    link = build_activesg_link(target_date)
    message = f"Please ballot, ignore if already have court for that week\n{link}"

    send_telegram_message(message)

    return {
        "statusCode": 200,
        "body": f"Message sent for {target_date} (SGT reference)"
    }


# For local testing
if __name__ == "__main__":
    print(lambda_handler())


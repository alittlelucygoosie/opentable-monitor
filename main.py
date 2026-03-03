import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import datetime
import os

# ===== SETTINGS =====

RESTAURANT = "Mahaniyom"
CITY = "Brookline"
PARTY_SIZE = 2

TIME_START = 18  # 6 PM
TIME_END = 19    # 7 PM

TO_PHONE = "+16176993228"

TWILIO_SID = os.environ["TWILIO_SID"]
TWILIO_TOKEN = os.environ["TWILIO_TOKEN"]
TWILIO_PHONE = os.environ["TWILIO_PHONE"]

# ====================


def get_next_saturday():
    today = datetime.date.today()
    days_ahead = (5 - today.weekday()) % 7
    return today + datetime.timedelta(days=days_ahead)


def check_opentable():

    date = get_next_saturday().strftime("%Y-%m-%d")

    url = "https://www.opentable.com/s"

    params = {
        "covers": PARTY_SIZE,
        "dateTime": f"{date}T18:00",
        "term": f"{RESTAURANT} {CITY}"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, params=params, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    times = soup.find_all("button", {"data-test": "time-slot"})

    available = []

    for t in times:
        txt = t.text.strip()
        hour = int(txt.split(":")[0])

        if TIME_START <= hour <= TIME_END:
            available.append(txt)

    return available


def send_text(times):

    client = Client(TWILIO_SID, TWILIO_TOKEN)

    msg = (
        "🎉 Mahaniyom reservation available!\n"
        f"Times: {', '.join(times)}\n"
        "Book now on OpenTable."
    )

    client.messages.create(
        body=msg,
        from_=TWILIO_PHONE,
        to=TO_PHONE
    )


def main():

    times = check_opentable()

    if times:
        send_text(times)
        print("Alert sent:", times)
    else:
        print("No availability.")


if __name__ == "__main__":
    main()

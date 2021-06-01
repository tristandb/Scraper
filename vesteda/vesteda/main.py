import requests
import smtplib
import os
import sys
import redis
from loguru import logger
import messagebird

logger.add(
    sys.stderr, format="{time} {level} {message}", filter="vesteda", level="INFO"
)

cache = redis.Redis(host="redis", port=6379, decode_responses=True)


def send_message(message="test_message"):
    logger.info(f"Sending message: {message}")
    client = messagebird.Client(str(os.environ.get("MESSAGEBIRD_CLIENT")))
    try:
        msg = client.message_create(
            str(os.environ.get("MESSAGEBIRD_ORIGINATOR")),
            str(os.environ.get("MESSAGEBIRD_DESTINATION")),
            message,
        )

    except messagebird.client.ErrorException as e:
        for error in e.errors:
            logger.debug(error)


def get_api(url):
    r = requests.get(url)
    return r.json()


def process_api_result(json):
    logger.info(f"Processing API result")
    for index in range(len(json["maps"])):
        woningen = json["maps"][index]
        for woning_id in woningen["aWoningen"]:
            woning = woningen["aWoningen"][woning_id]

            # Get current status and update if is not None
            current_status = cache.get(woning_id)
            if current_status is None:
                current_status = woning["Woning_Status"]
                cache.set(woning_id, current_status)

            # Chack if has changed, send message
            if current_status != woning["Woning_Status"] and woning[
                "Woning_Status"
            ] not in ["Verhuurd"]:
                message = f"""Update voor Vesteda woning {woning["Straatnaam"]} {woning["Huisnummer"]}, veranderd naar status {woning["Woning_Status"]}, prijs € {woning["Woning_Prijs"]}."""
                send_message(message)
            cache.set(woning_id, woning["Woning_Status"])


def main():
    result = get_api(
        url="https://account.hureninnoorderhaven.nl/feed/mediamaps.js?mids=1209,1210,1211,1212,1213,1214&woninginfo=true&woningmedia=true&woningmediadoc=true&woningtype=true&woningtypemediadoc=true&woningtypemedia=true&extrainfo=true"
    )
    process_api_result(result)


if __name__ == "__main__":
    main()
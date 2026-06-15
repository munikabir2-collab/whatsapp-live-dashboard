import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


def send_whatsapp_message(number: str, message: str):

    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

    # 🔥 DEBUG HERE (OUTSIDE DICT)
    print("TOKEN:", TOKEN)

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    return response.json()
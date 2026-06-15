import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def chat_with_ai(message: str):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful WhatsApp SaaS bot."},
            {"role": "user", "content": message}
        ]
    )

    return response["choices"][0]["message"]["content"]
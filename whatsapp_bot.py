from ai_bot import chat_with_ai

async def handle_message(sock, msg, jid):

    text = msg.message.get("conversation") if msg.message else None
    if not text:
        return

    reply = chat_with_ai(text)

    await sock.sendMessage(jid, {
        "text": reply
    })
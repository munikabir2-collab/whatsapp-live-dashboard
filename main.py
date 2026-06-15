from fastapi import FastAPI, WebSocket
from fastapi import Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocketDisconnect
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from sqlalchemy.orm import Session

from moviepy.editor import TextClip, CompositeVideoClip

from database import Base, engine, get_db, SessionLocal
from models import Message

from broadcaster import manager

from whatsapp_service import send_whatsapp_message

import uvicorn


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI()

templates = Jinja2Templates(directory="templates")


# =====================================================
# STARTUP
# =====================================================

@app.on_event("startup")
def startup():

    # Create database tables automatically
    Base.metadata.create_all(bind=engine)

    print("✅ Database Connected")


# =====================================================
# HOME PAGE
# =====================================================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    db = SessionLocal()

    try:

        # Get all messages
        messages = db.query(Message).all()

    finally:

        db.close()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "messages": messages
        }
    )


# =====================================================
# SEND WHATSAPP MESSAGE
# =====================================================

@app.post("/send")
async def send_message(
    text: str = Form(...),
    db: Session = Depends(get_db)
):

    try:

        # Send message to WhatsApp
        result = send_whatsapp_message(
            number="917061691018",
            message=text
        )

        print("✅ WhatsApp Response:")
        print(result)

        whatsapp_id = None

        # Get WhatsApp message id
        if (
            isinstance(result, dict)
            and "messages" in result
            and len(result["messages"]) > 0
        ):
            whatsapp_id = result["messages"][0].get("id")

        # Save message in database
        msg = Message(
            text=text,
            sender="user",
            receiver="917061691018",
            status="sent",
            whatsapp_id=whatsapp_id
        )

        db.add(msg)
        db.commit()
        db.refresh(msg)

        # Broadcast live message
        await manager.broadcast({
            "type": "new_message",
            "id": msg.id,
            "text": msg.text,
            "status": msg.status
        })

        return {
            "status": "sent",
            "message": text,
            "whatsapp": result
        }

    except Exception as e:

        print("❌ SEND ERROR:", str(e))

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )


# =====================================================
# WEBSOCKET
# =====================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await manager.connect(websocket)

    print("✅ WebSocket Connected")

    try:

        while True:

            # Receive data from frontend
            data = await websocket.receive_text()

            print("📩 Received:", data)

            # Broadcast live message
            await manager.broadcast({
                "type": "live_message",
                "text": data
            })

    except WebSocketDisconnect:

        manager.disconnect(websocket)

        print("❌ WebSocket Disconnected")


# =====================================================
# WHATSAPP VERIFY
# =====================================================

@app.get("/webhook")
async def verify(request: Request):

    VERIFY_TOKEN = "muni4767"

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:

        return int(challenge)

    return {"error": "Verification failed"}


# =====================================================
# WHATSAPP WEBHOOK
# =====================================================

@app.post("/webhook")
async def webhook(request: Request):

    data = await request.json()

    print("🔥 WHATSAPP WEBHOOK:")
    print(data)

    for entry in data.get("entry", []):

        for change in entry.get("changes", []):

            value = change.get("value", {})

            # =========================================
            # STATUS UPDATE
            # =========================================

            for status in value.get("statuses", []):

                msg_id = status.get("id")
                new_status = status.get("status")

                db = SessionLocal()

                try:

                    msg = db.query(Message).filter_by(
                        whatsapp_id=msg_id
                    ).first()

                    if msg:

                        msg.status = new_status

                        db.commit()

                        # Live status update
                        await manager.broadcast({
                            "type": "status_update",
                            "id": msg.id,
                            "status": new_status
                        })

                except Exception as e:

                    print("❌ STATUS UPDATE ERROR:", str(e))

                finally:

                    db.close()

            # =========================================
            # INCOMING MESSAGE
            # =========================================

            for incoming in value.get("messages", []):

                sender = incoming.get("from")

                text_data = incoming.get("text", {})

                incoming_text = text_data.get("body")

                if incoming_text:

                    db = SessionLocal()

                    try:

                        new_msg = Message(
                            text=incoming_text,
                            sender=sender,
                            receiver="me",
                            status="received",
                            whatsapp_id=incoming.get("id")
                        )

                        db.add(new_msg)
                        db.commit()
                        db.refresh(new_msg)

                        # Broadcast incoming message
                        await manager.broadcast({
                            "type": "incoming_message",
                            "id": new_msg.id,
                            "text": new_msg.text,
                            "status": new_msg.status
                        })

                    except Exception as e:

                        print("❌ INCOMING ERROR:", str(e))

                    finally:

                        db.close()

    return {"ok": True}


# =====================================================
# MESSENGER VERIFY
# =====================================================

@app.get("/messenger/webhook")
async def messenger_verify(request: Request):

    VERIFY_TOKEN = "muni4767"

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:

        return int(challenge)

    return {"error": "Verification failed"}


# =====================================================
# MESSENGER WEBHOOK
# =====================================================

@app.post("/messenger/webhook")
async def messenger_webhook(request: Request):

    data = await request.json()

    print("🔥 MESSENGER WEBHOOK:")
    print(data)

    for entry in data.get("entry", []):

        for messaging in entry.get("messaging", []):

            message = messaging.get("message")

            if not message:
                continue

            text = message.get("text")

            if text:

                await manager.broadcast({
                    "type": "messenger_message",
                    "text": text
                })

    return {"status": "ok"}


# =====================================================
# CREATE VIDEO FUNCTION
# =====================================================

def create_video(text, output_path="output.mp4"):

    try:

        # Create text clip
        clip = TextClip(
            text=text,
            fontsize=60,
            color="white",
            size=(720, 1280),
            bg_color="black",
            method="caption"
        )

        # Create 5-second video
        video = CompositeVideoClip([
            clip.set_duration(5)
        ])

        # Export video
        video.write_videofile(
            output_path,
            fps=24
        )

        print("✅ Video Created")

        return output_path

    except Exception as e:

        print("❌ VIDEO ERROR:", str(e))

        return None


# =====================================================
# VIDEO TEST ROUTE
# =====================================================

@app.get("/video")
def video_test():

    output = create_video("Hello Munilal")

    if output:

        return {
            "status": "success",
            "file": output
        }

    return {
        "status": "failed"
    }


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
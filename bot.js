import makeWASocket, {
  useMultiFileAuthState,
  DisconnectReason
} from "@whiskeysockets/baileys";

import qrcode from "qrcode-terminal";

// START BOT
async function startBot() {

  // AUTH
  const { state, saveCreds } =
    await useMultiFileAuthState("auth_info_baileys");

  // SOCKET
  const sock = makeWASocket({
    auth: state
  });

  // CONNECTION UPDATE
  sock.ev.on("connection.update", async (update) => {

    const {
      connection,
      lastDisconnect,
      qr
    } = update;

    // SHOW QR
    if (qr) {

      console.log("\n📱 Scan QR Code Below:\n");

      qrcode.generate(qr, {
        small: true
      });
    }

    // CONNECTED
    if (connection === "open") {

      console.log("✅ WhatsApp Bot Connected Successfully");
    }

    // DISCONNECTED
    else if (connection === "close") {

      console.log("❌ Connection Closed");

      const shouldReconnect =
        lastDisconnect?.error?.output?.statusCode !==
        DisconnectReason.loggedOut;

      if (shouldReconnect) {

        console.log("🔄 Reconnecting...");
        startBot();
      }
    }
  });

  // SAVE CREDS
  sock.ev.on("creds.update", saveCreds);

  // MESSAGE LISTENER
  sock.ev.on("messages.upsert", async ({ messages }) => {

    try {

      const msg = messages[0];

      if (!msg.message) return;

      // SENDER
      const sender = msg.key.remoteJid;

      // MESSAGE TEXT
      const text =
        msg.message.conversation ||
        msg.message.extendedTextMessage?.text ||
        "";

      console.log("📩 Message:", text);

      // =========================
      // AUTO REPLY COMMANDS
      // =========================

      // HI
      if (text.toLowerCase() === "hi") {

        await sock.sendMessage(sender, {
          text: "Hello 👋 Bot Active"
        });
      }

      // HELLO
      else if (text.toLowerCase() === "hello") {

        await sock.sendMessage(sender, {
          text: "Hi 😊 How are you?"
        });
      }

      // MENU
      else if (text.toLowerCase() === "menu") {

        await sock.sendMessage(sender, {
          text:
`📋 BOT MENU

1. hi
2. hello
3. time
4. owner
5. ping`
        });
      }

      // TIME
      else if (text.toLowerCase() === "time") {

        const time = new Date().toLocaleString();

        await sock.sendMessage(sender, {
          text: `🕒 Current Time:\n${time}`
        });
      }

      // OWNER
      else if (text.toLowerCase() === "owner") {

        await sock.sendMessage(sender, {
          text: "👑 Bot Owner: Munilal"
        });
      }

      // PING
      else if (text.toLowerCase() === "ping") {

        await sock.sendMessage(sender, {
          text: "🏓 Pong"
        });
      }

    } catch (error) {

      console.log("❌ Error:", error);
    }
  });
}

// RUN BOT
startBot();
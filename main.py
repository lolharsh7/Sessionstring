import os
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

# --- FLASK SERVER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT LOGIC ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Initialize client without starting it immediately
bot = TelegramClient('bot_session', API_ID, API_HASH)

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(
        "👋 **Welcome to Session Generator!**\n\n"
        "Send your phone number in international format.\n"
        "Example: `+919876543210`"
    )

@bot.on(events.NewMessage)
async def handle_phone(event):
    if event.text.startswith('+'):
        phone = event.text.strip()
        # Create a temporary client for session generation
        temp_client = TelegramClient(StringSession(), API_ID, API_HASH)
        await temp_client.connect()
        
        try:
            await temp_client.send_code_request(phone)
            async with bot.conversation(event.chat_id) as conv:
                await conv.send_message("Please send the **OTP** you received (Example: 12345):")
                otp_msg = await conv.get_response()
                otp = otp_msg.text.replace(" ", "")
                
                try:
                    await temp_client.sign_in(phone, otp)
                except SessionPasswordNeededError:
                    await conv.send_message("2-Factor Authentication is ON. Enter your password:")
                    pw_msg = await conv.get_response()
                    await temp_client.sign_in(password=pw_msg.text)
                
                string_session = temp_client.session.save()
                await temp_client.send_message("me", f"**Your Session String:**\n\n`{string_session}`\n\nKeep it safe!")
                await event.respond("✅ **Success!** Check your **Saved Messages** for the string.")
                
        except Exception as e:
            await event.respond(f"❌ Error: {str(e)}")
        finally:
            await temp_client.disconnect()

async def main():
    # Start the bot properly inside the loop
    await bot.start(bot_token=BOT_TOKEN)
    print("Bot is running...")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    # Start Flask thread
    Thread(target=run_flask, daemon=True).start()
    
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
async def handle_phone(event):
    if event.text.startswith('+'):
        phone = event.text.strip()
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        
        try:
            await client.send_code_request(phone)
            async with bot.conversation(event.chat_id) as conv:
                await conv.send_message("Please send the **OTP** you received (Example: 12345):")
                otp_msg = await conv.get_response()
                otp = otp_msg.text.replace(" ", "")
                
                try:
                    await client.sign_in(phone, otp)
                except SessionPasswordNeededError:
                    await conv.send_message("2-Factor Authentication is ON. Enter your password:")
                    pw_msg = await conv.get_response()
                    await client.sign_in(password=pw_msg.text)
                
                # Generate and Send String
                string_session = client.session.save()
                await client.send_message("me", f"**Your Session String:**\n\n`{string_session}`\n\nKeep it safe!")
                await event.respond("✅ **Success!** Check your **Saved Messages** for the string.")
                
        except Exception as e:
            await event.respond(f"❌ Error: {str(e)}")
        finally:
            await client.disconnect()

if __name__ == "__main__":
    # Start Flask in a separate thread
    Thread(target=run_flask).start()
    print("Bot is running...")
    bot.run_until_disconnected()

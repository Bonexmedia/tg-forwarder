# forwarder.py - Advanced Cleaner + Replacer (Render-compatible)
from telethon import TelegramClient, events
import os
import re
import asyncio

# === CONFIG FROM ENVIRONMENT VARIABLES (set these in Render dashboard) ===
API_ID       = int(os.environ['API_ID'])
API_HASH     = os.environ['API_HASH']
PHONE        = os.environ['PHONE']
SOURCE       = os.environ['SOURCE_CHANNEL']      # can be username or ID
TARGET       = os.environ['TARGET_CHANNEL']      # can be username or ID

# ←←←←←←←←←←←←←←←←←  EDIT THESE 3 LINES BELOW  ←←←←←←←←←←←←←←←←←
REPLACE_USERNAME = "@Cryptoinsiderbets"           # every @username becomes this
REMOVE_TELEGRAM_LINKS = True                      # False to keep t.me links

# Keywords to replace (case-insensitive)
KEYWORDS_TO_REPLACE = {
    "shit": "****",
    "fuck": "****",
    "scam": "opportunity",
    "free money": "hard work",
    # add more here
}
# ============================================================

client = TelegramClient('sess', API_ID, API_HASH)

# Regex patterns
TG_LINKS = re.compile(r'(https?://)?(t\.me|telegram\.me|telegram\.dog)/[^\s]+', re.IGNORECASE)
USERNAME_MENTION = re.compile(r'@\w+')

def clean_text(text: str) -> str:
    if not text:
        return text

    # 1. Keyword replacement
    for bad, good in KEYWORDS_TO_REPLACE.items():
        text = re.sub(re.escape(bad), good, text, flags=re.IGNORECASE)

    # 2. Remove Telegram links
    if REMOVE_TELEGRAM_LINKS:
        text = TG_LINKS.sub('', text)

    # 3. Replace every @username
    text = USERNAME_MENTION.sub(REPLACE_USERNAME, text)

    return text.strip()

@client.on(events.NewMessage(chats=SOURCE)
async def handler(event):
    try:
        msg = event.message

        # If already forwarded → just forward (keeps original forward tag)
        if msg.fwd_from:
            await client.forward_messages(TARGET, msg)
            print(f"Forwarded (original tag kept) → {msg.id}")
            return

        # Normal message → clean it
        cleaned_text = clean_text(msg.message) if msg.message else None
        file = await msg.download_media() if msg.media else None

        await client.send_message(
            entity=TARGET,
            message=cleaned_text or '',  # Telegram requires non-None message if no file
            file=file,
            formatting_entities=msg.entities,
            silent=True
        )
        print(f"Cleaned & sent → {msg.id}")

    except Exception as e:
        print(f"Error processing message {event.message.id}: {e}")

# ———————————————— NON-INTERACTIVE LOGIN FOR RENDER ————————————————
async def main():
    print("Advanced Forwarder starting...")

    # Try to login without any prompts
    await client.start(
        phone=PHONE,
        code_callback=lambda: os.environ['TG_CODE'],           # ← reads the code from env var
    )

    me = await client.get_me()
    print(f"Successfully logged in as {me.first_name} (@{me.username or 'no username'})")
    print(f"Watching {SOURCE} → {TARGET}")
    print(f"• All @usernames replaced with → {REPLACE_USERNAME}")
    print(f"• Telegram links removed → {REMOVE_TELEGRAM_LINKS}")

    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())

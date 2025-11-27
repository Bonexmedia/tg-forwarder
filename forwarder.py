# forwarder.py - Advanced Cleaner + Replacer (Render-ready, no 2FA)
from telethon import TelegramClient, events
import os
import re
import asyncio

# === CONFIG FROM ENVIRONMENT VARIABLES ===
API_ID   = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
PHONE    = os.environ['PHONE']
SOURCE   = os.environ['SOURCE_CHANNEL']
TARGET   = os.environ['TARGET_CHANNEL']

# ←←←←←←←←←←←←←←←←←  EDIT THESE  ←←←←←←←←←←←←←←←←
REPLACE_USERNAME      = "@Cryptoinsiderbets"   # every @username becomes this
REMOVE_TELEGRAM_LINKS = True                   # False = keep t.me links

KEYWORDS_TO_REPLACE = {
    "shit": "****",
    "fuck": "****",
    "scam": "opportunity",
    "free money": "hard work",
    # add more if you want
}

client = TelegramClient('sess', API_ID, API_HASH)

# Regex
TG_LINKS         = re.compile(r'(https?://)?(t\.me|telegram\.me|telegram\.dog)/[^\s]+', re.IGNORECASE)
USERNAME_MENTION = re.compile(r'@\w+')

def clean_text(text: str) -> str:
    if not text:
        return text

    for bad, good in KEYWORDS_TO_REPLACE.items():
        text = re.sub(re.escape(bad), good, text, flags=re.IGNORECASE)

    if REMOVE_TELEGRAM_LINKS:
        text = TG_LINKS.sub('', text)

    text = USERNAME_MENTION.sub(REPLACE_USERNAME, text)
    return text.strip()

# ←←←←←←←←←←←  THIS LINE WAS MISSING A )  ←←←←←←←←←←←
@client.on(events.NewMessage(chats=SOURCE))
async def handler(event):
    try:
        msg = event.message

        # Keep original forward tag if message was already forwarded
        if msg.fwd_from:
            await client.forward_messages(TARGET, msg)
            print(f"Forwarded (original tag kept) → {msg.id}")
            return

        # Clean normal messages
        cleaned_text = clean_text(msg.message) if msg.message else None
        file = await msg.download_media() if msg.media else None

        await client.send_message(
            entity=TARGET,
            message=cleaned_text or '',
            file=file,
            formatting_entities=msg.entities,
            silent=True
        )
        print(f"Cleaned & sent → {msg.id}")

    except Exception as e:
        print(f"Error: {e}")

# ———————————————— NON-INTERACTIVE LOGIN ————————————————
async def main():
    print("Advanced Forwarder starting...")

    await client.start(
        phone=PHONE,
        code_callback=lambda: os.environ['TG_CODE']
    )

    me = await client.get_me()
    print(f"Logged in as {me.first_name} (@{me.username or 'no username'})")
    print(f"Watching {SOURCE} → {TARGET}")
    print(f"All @usernames → {REPLACE_USERNAME}")
    print(f"t.me links removed → {REMOVE_TELEGRAM_LINKS}")

    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())

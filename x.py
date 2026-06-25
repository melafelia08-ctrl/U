import sqlite3
import uuid

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8217841082:AAH6Ju6FlJbudPxsjvRBTeKH5WPZsoPy3Uw"

CHANNEL_USERNAME = "@sodohuyall"
BOT_USERNAME = "Sodohuuuuubot"

ADMIN_ID = 8502412097

db = sqlite3.connect("files.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS files(
    code TEXT PRIMARY KEY,
    file_id TEXT,
    file_type TEXT
)
""")
db.commit()


async def is_joined(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in [
            "member",
            "administrator",
            "creator"
        ]
    except:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    joined = await is_joined(context.bot, user.id)

    if not joined:
        await update.message.reply_text(
            f"❌ Pehle channel join karo:\nhttps://t.me/sodohuyall"
        )
        return

    if context.args:
        code = context.args[0]

        cur.execute(
            "SELECT file_id,file_type FROM files WHERE code=?",
            (code,)
        )

        row = cur.fetchone()

        if not row:
            await update.message.reply_text("❌ File not found.")
            return

        file_id, file_type = row

        if file_type == "document":
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=file_id
            )

        elif file_type == "video":
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=file_id
            )

        elif file_type == "photo":
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=file_id
            )

        return

    await update.message.reply_text(
        "✅ Bot working.\nAdmin file upload kar sakta hai."
    )


async def upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text(
            "❌ Only admin can upload files."
        )
        return

    file_id = None
    file_type = None

    if update.message.document:
        file_id = update.message.document.file_id
        file_type = "document"

    elif update.message.video:
        file_id = update.message.video.file_id
        file_type = "video"

    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_type = "photo"

    if not file_id:
        return

    code = str(uuid.uuid4())[:8]

    cur.execute(
        "INSERT INTO files VALUES(?,?,?)",
        (code, file_id, file_type)
    )
    db.commit()

    link = f"https://t.me/{BOT_USERNAME}?start={code}"

    await update.message.reply_text(
        f"✅ File Saved\n\n🔗 {link}"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.Document
            | filters.VIDEO
            | filters.PHOTO,
            upload_file
        )
    )

    print("Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
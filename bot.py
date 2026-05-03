print("BOT STARTING...")
import json, os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

BOT_TOKEN = "8689386145:AAF87ntS8S3RKV8VSHj4FdvkjF4yIDnSJ3Y"

ADMIN_IDS = [7839961753, 8000127916]

GROUP_ID = -1003829518602
CHANNEL_ID = -1003762962484
CHANNEL_USERNAME = "@jaiminjunction"
GROUP_USERNAME = "@jaimincommunity"

PLAYERS_FILE = "players.json"
PENDING_FILE = "pending.json"
CONFIG_FILE = "config.json"


def load(file, default):
    if not os.path.exists(file):
        save(file, default)
        return default
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        save(file, default)
        return default


def save(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


players = load(PLAYERS_FILE, {})
pending = load(PENDING_FILE, {})
config = load(CONFIG_FILE, {"registration_open": True})


def is_admin(user_id):
    return user_id in ADMIN_IDS


def safe_user(update: Update):
    return update.effective_user if update and update.effective_user else None


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = safe_user(update)
    if not user or not update.message:
        return
    await update.message.reply_text(f"🆔 Your Telegram ID:\n`{user.id}`", parse_mode="Markdown")


async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    chat = update.effective_chat
    await update.message.reply_text(
        f"💬 Chat ID:\n`{chat.id}`\n\n"
        f"Chat Type: `{chat.type}`\n"
        f"Chat Title: `{chat.title or 'Private Chat'}`",
        parse_mode="Markdown"
    )


async def check_join(bot, user_id):
    try:
        g = await bot.get_chat_member(GROUP_ID, user_id)
        c = await bot.get_chat_member(CHANNEL_ID, user_id)
        good_status = ["member", "administrator", "creator"]
        return g.status in good_status and c.status in good_status
    except Exception as e:
        print("JOIN CHECK ERROR:", e)
        return False


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Register / Confirm", callback_data="confirm_register")],
        [
            InlineKeyboardButton("📌 Status", callback_data="menu_status"),
            InlineKeyboardButton("👤 Profile", callback_data="menu_profile")
        ],
        [InlineKeyboardButton("ℹ️ Help", callback_data="menu_help")]
    ])


def join_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
        [InlineKeyboardButton("👥 Join Group", url=f"https://t.me/{GROUP_USERNAME.replace('@','')}")],
        [InlineKeyboardButton("✅ I Joined", callback_data="check_join")]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = safe_user(update)
    if not user or not update.message:
        return

    user_id = str(user.id)

    if not config.get("registration_open", True):
        await update.message.reply_text("❌ Registration abhi closed hai.")
        return

    joined = await check_join(context.bot, user.id)

    if not joined:
        await update.message.reply_text(
            "⚠️ Registration ke liye Group aur Channel dono join karna compulsory hai.\n\n"
            "Join karne ke baad ✅ I Joined dabao.",
            reply_markup=join_menu()
        )
        return

    username = f"@{user.username}" if user.username else "No Username"

    if user_id in players:
        await update.message.reply_text(
            f"✅ Aap already registered ho.\n\n👤 {user.full_name}\n🔗 {username}",
            reply_markup=main_menu()
        )
        return

    if user_id in pending:
        await update.message.reply_text(
            "⏳ Aapki registration request admin approval ke liye pending hai.",
            reply_markup=main_menu()
        )
        return

    await update.message.reply_text(
        f"🏏 Registration Details\n\n"
        f"👤 Name: {user.full_name}\n"
        f"🔗 Username: {username}\n\n"
        f"Confirm karne ke liye button dabao.",
        reply_markup=main_menu()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()
    user = query.from_user
    if not user:
        return

    user_id = str(user.id)

    if query.data == "menu_status":
        if user_id in players:
            await query.edit_message_text("✅ Aap registered aur approved ho.", reply_markup=main_menu())
        elif user_id in pending:
            await query.edit_message_text("⏳ Aapki request pending hai.", reply_markup=main_menu())
        else:
            await query.edit_message_text("❌ Aap registered nahi ho. Register button dabao.", reply_markup=main_menu())
        return

    if query.data == "menu_profile":
        if user_id not in players:
            await query.edit_message_text("❌ Profile nahi mila. Pehle register karo.", reply_markup=main_menu())
        else:
            p = players[user_id]
            await query.edit_message_text(
                f"👤 Player Profile\n\n"
                f"Name: {p['name']}\n"
                f"Username: {p['username']}\n"
                f"ID: {p['id']}\n"
                f"Status: Approved ✅",
                reply_markup=main_menu()
            )
        return

    if query.data == "menu_help":
        await query.edit_message_text(
            "🏏 Player Commands\n"
            "/start - Register / Open menu\n"
            "/status - Check status\n"
            "/profile - Profile\n"
            "/help - Help\n"
            "/myid - Your ID\n"
            "/chatid - Group/Channel ID\n\n"
            "👑 Admin Commands\n"
            "/players\n"
            "/pending\n"
            "/broadcast message\n"
            "/remove user_id\n"
            "/open\n"
            "/close\n"
            "/export\n"
            "/backup\n"
            "/restore",
            reply_markup=main_menu()
        )
        return

    if query.data == "check_join":
        joined = await check_join(context.bot, user.id)

        if not joined:
            await query.edit_message_text(
                "❌ Abhi bhi join detect nahi hua.\n\n"
                "✅ Bot ko Group aur Channel dono me admin banao.\n"
                "✅ GROUP_ID aur CHANNEL_ID real daalo.\n"
                "✅ Phir bot restart karo.",
                reply_markup=join_menu()
            )
            return

        username = f"@{user.username}" if user.username else "No Username"

        await query.edit_message_text(
            f"🏏 Registration Details\n\n"
            f"👤 Name: {user.full_name}\n"
            f"🔗 Username: {username}\n\n"
            f"Confirm karne ke liye button dabao.",
            reply_markup=main_menu()
        )
        return

    if query.data == "confirm_register":
        joined = await check_join(context.bot, user.id)

        if not joined:
            await query.edit_message_text(
                "❌ Pehle Group aur Channel dono join karo.",
                reply_markup=join_menu()
            )
            return

        if user_id in players:
            await query.edit_message_text("✅ Aap already registered ho.", reply_markup=main_menu())
            return

        if user_id in pending:
            await query.edit_message_text("⏳ Request already pending hai.", reply_markup=main_menu())
            return

        pending[user_id] = {
            "id": user.id,
            "name": user.full_name,
            "username": f"@{user.username}" if user.username else "No Username",
            "date": datetime.now().strftime("%d-%m-%Y %I:%M %p")
        }
        save(PENDING_FILE, pending)

        await query.edit_message_text(
            "✅ Request admin ke paas approval ke liye bhej di gayi hai.",
            reply_markup=main_menu()
        )

        admin_buttons = [[
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]]

        for admin in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    admin,
                    f"🆕 New Player Registration Request\n\n"
                    f"👤 Name: {pending[user_id]['name']}\n"
                    f"🔗 Username: {pending[user_id]['username']}\n"
                    f"🆔 ID: {user_id}",
                    reply_markup=InlineKeyboardMarkup(admin_buttons)
                )
            except Exception as e:
                print("ADMIN MSG ERROR:", e)
        return

    if query.data.startswith("approve_"):
        if not is_admin(user.id):
            await query.answer("Admin only", show_alert=True)
            return

        pid = query.data.replace("approve_", "")

        if pid not in pending:
            await query.edit_message_text("❌ Request not found.")
            return

        player = pending.pop(pid)
        player["approved_date"] = datetime.now().strftime("%d-%m-%Y %I:%M %p")
        players[pid] = player

        save(PLAYERS_FILE, players)
        save(PENDING_FILE, pending)

        await query.edit_message_text(
            f"✅ Player Approved\n\n👤 {player['name']}\n🔗 {player['username']}"
        )

        try:
            await context.bot.send_message(
                int(pid),
                "🎉 Congratulations!\n\n✅ Aapki registration approve ho gayi hai."
            )
        except:
            pass

        try:
            await context.bot.send_message(
                CHANNEL_ID,
                f"🏏 New Player Registered\n\n"
                f"👤 Name: {player['name']}\n"
                f"🔗 Username: {player['username']}\n"
                f"✅ Status: Approved"
            )
        except Exception as e:
            print("CHANNEL MSG ERROR:", e)
        return

    if query.data.startswith("reject_"):
        if not is_admin(user.id):
            await query.answer("Admin only", show_alert=True)
            return

        pid = query.data.replace("reject_", "")

        if pid in pending:
            player = pending.pop(pid)
            save(PENDING_FILE, pending)

            await query.edit_message_text(f"❌ Player rejected: {player['name']}")

            try:
                await context.bot.send_message(int(pid), "❌ Aapki registration request reject kar di gayi hai.")
            except:
                pass
        return


async def players_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = safe_user(update)
    if not user or not update.message or not is_admin(user.id):
        return

    if not players:
        await update.message.reply_text("❌ Koi player registered nahi hai.")
        return

    text = "✅ Registered Players List:\n\n"
    for i, p in enumerate(players.values(), 1):
        text += f"{i}. {p['name']} | {p['username']} | ID: {p['id']}\n"

    await update.message.reply_text(text)


async def pending_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = safe_user(update)
    if not user or not update.message or not is_admin(user.id):
        return

    if not pending:
        await update.message.reply_text("✅ Koi pending request nahi hai.")
        return

    text = "⏳ Pending Players:\n\n"
    for i, p in enumerate(pending.values(), 1):
        text += f"{i}. {p['name']} | {p['username']} | ID: {p['id']}\n"

    await update.message.reply_text(text)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = safe_user(update)
    if not user or not update.message:
        return

    uid = str(user.id)

    if uid in players:
        await update.message.reply_text("✅ Aap registered aur approved ho.")
    elif uid in pending:
        await update.message.reply_text("⏳ Aapki request pending hai.")
    else:
        await update.message.reply_text("❌ Aap registered nahi ho. /start bhejo.")


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = safe_user(update)
    if not user or not update.message:
        return

    uid = str(user.id)

    if uid not in players:
        await update.message.reply_text("❌ Profile nahi mila. Pehle register karo.")
        return

    p = players[uid]
    await update.message.reply_text(
        f"👤 Player Profile\n\n"
        f"Name: {p['name']}\n"
        f"Username: {p['username']}\n"
        f"ID: {p['id']}\n"
        f"Status: Approved ✅"
    )


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = safe_user(update)
    if not user or not update.message or not is_admin(user.id):
        return

    if not context.args:
        await update.message.reply_text("Use: /remove user_id")
        return

    uid = context.args[0]

    if uid in players:
        removed = players.pop(uid)
        save(PLAYERS_FILE, players)
        await update.message.reply_text(f"✅ Removed: {removed['name']}")
    else:
        await update.message.reply_text("❌ Player not found.")


async def open_reg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = safe_user(update)
    if not user or not update.message or not is_admin(user.id):
        return

    config["registration_open"] = True
    save(CONFIG_FILE, config)
    await update.message.reply_text("✅ Registration open kar diya.")


async def close_reg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = safe_user(update)
    if not user or not update.message or not is_admin(user.id):
        return

    config["registration_open"] = False
    save(CONFIG_FILE, config)
    await update.message.reply_text("🔒 Registration close kar diya.")


async def export_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = safe_user(update)
    if not user or not update.message or not is_admin(user.id):
        return

    filename = "players_export.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Registered Players\n\n")
        for i, p in enumerate(players.values(), 1):
            f.write(f"{i}. {p['name']} | {p['username']} | ID: {p['id']}\n")

    with open(filename, "rb") as f:
        await update.message.reply_document(f)


async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = safe_user(update)
    if not user or not update.message or not is_admin(user.id):
        return

    for file in [PLAYERS_FILE, PENDING_FILE, CONFIG_FILE]:
        if not os.path.exists(file):
            save(file, {})
        with open(file, "rb") as f:
            await update.message.reply_document(f)


async def restore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = safe_user(update)
    if not user or not update.message or not is_admin(user.id):
        return

    await update.message.reply_text(
        "Restore ke liye JSON file bhejo aur caption me likho:\n\n"
        "restore players\n"
        "restore pending\n"
        "restore config"
    )


async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = safe_user(update)
    if not user or not update.message or not is_admin(user.id):
        return

    caption = (update.message.caption or "").lower().strip()

    if not caption.startswith("restore"):
        return

    doc = update.message.document
    if not doc:
        return

    file = await doc.get_file()
    path = f"restore_{doc.file_name}"
    await file.download_to_drive(path)

    global players, pending, config

    try:
        data = load(path, {})
    except:
        await update.message.reply_text("❌ Invalid JSON file.")
        return

    if "players" in caption:
        players = data
        save(PLAYERS_FILE, players)
        await update.message.reply_text("✅ Players restore ho gaye.")

    elif "pending" in caption:
        pending = data
        save(PENDING_FILE, pending)
        await update.message.reply_text("✅ Pending restore ho gaya.")

    elif "config" in caption:
        config = data
        save(CONFIG_FILE, config)
        await update.message.reply_text("✅ Config restore ho gaya.")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = safe_user(update)
    if not user or not update.message or not is_admin(user.id):
        return

    msg = " ".join(context.args)

    if not msg:
        await update.message.reply_text("Use: /broadcast message")
        return

    count = 0
    for uid in players.keys():
        try:
            await context.bot.send_message(int(uid), msg)
            count += 1
        except:
            pass

    await update.message.reply_text(f"✅ Broadcast sent to {count} players.")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    await update.message.reply_text(
        "🏏 Player Commands\n"
        "/start - Register / Open menu\n"
        "/status - Check status\n"
        "/profile - Profile\n"
        "/help - Help\n"
        "/myid - Your ID\n"
        "/chatid - Group/Channel ID\n\n"
        "👑 Admin Commands\n"
        "/players\n"
        "/pending\n"
        "/broadcast message\n"
        "/remove user_id\n"
        "/open\n"
        "/close\n"
        "/export\n"
        "/backup\n"
        "/restore"
    )


async def set_commands(app):
    await app.bot.set_my_commands([
        BotCommand("start", "Register / Open menu"),
        BotCommand("status", "Check approval status"),
        BotCommand("profile", "Show profile"),
        BotCommand("help", "Show help"),
        BotCommand("myid", "Show your Telegram ID"),
        BotCommand("chatid", "Show current chat ID"),
        BotCommand("players", "Admin: players list"),
        BotCommand("pending", "Admin: pending requests"),
        BotCommand("broadcast", "Admin: broadcast message"),
        BotCommand("remove", "Admin: remove player"),
        BotCommand("open", "Admin: open registration"),
        BotCommand("close", "Admin: close registration"),
        BotCommand("export", "Admin: export players"),
        BotCommand("backup", "Admin: backup files"),
        BotCommand("restore", "Admin: restore files"),
    ])


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print("ERROR:", context.error)


import asyncio

def main():
    try:
        print("Initializing bot...")

        app = Application.builder().token(BOT_TOKEN).post_init(set_commands).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("status", status))
        app.add_handler(CommandHandler("profile", profile))
        app.add_handler(CommandHandler("help", help_cmd))
        app.add_handler(CommandHandler("myid", myid))
        app.add_handler(CommandHandler("chatid", chatid))

        app.add_handler(CommandHandler("players", players_cmd))
        app.add_handler(CommandHandler("pending", pending_cmd))
        app.add_handler(CommandHandler("broadcast", broadcast))
        app.add_handler(CommandHandler("remove", remove))
        app.add_handler(CommandHandler("open", open_reg))
        app.add_handler(CommandHandler("close", close_reg))
        app.add_handler(CommandHandler("export", export_players))
        app.add_handler(CommandHandler("backup", backup))
        app.add_handler(CommandHandler("restore", restore))

        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.Document.ALL, document_handler))

        app.add_error_handler(error_handler)

        print("Bot running...")
        app.run_polling()

    except Exception as e:
        print("🔥 ERROR:", e)


if __name__ == "__main__":
    main()
 

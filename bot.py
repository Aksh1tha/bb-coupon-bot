from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os, json

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5877824106
CHANNEL_USERNAME = "@ugcwaksh"

STOCK_FILE = "stock.txt"
USED_FILE = "used.json"
PENDING_FILE = "pending.json"


def load(file, default):
    if not os.path.exists(file):
        return default
    with open(file, "r") as f:
        return json.load(f)


def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)


def load_stock():
    if not os.path.exists(STOCK_FILE):
        return []
    with open(STOCK_FILE) as f:
        return [x.strip() for x in f if x.strip()]


def save_stock(stock):
    with open(STOCK_FILE, "w") as f:
        for c in stock:
            f.write(c + "\n")


async def is_member(bot, user_id):
    try:
        m = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)

    if not await is_member(context.bot, user.id):
        kb = [
            [InlineKeyboardButton("📢 Join Channel", url="https://t.me/ugcwaksh")],
            [InlineKeyboardButton("✅ I've Joined", callback_data="check")]
        ]
        await update.message.reply_text("Join channel to continue", reply_markup=InlineKeyboardMarkup(kb))
        return

    used = load(USED_FILE, {})
    if uid in used:
        await update.message.reply_text(f"🎟 You already got:\n{used[uid]}")
        return

    text = (
        "💸 *Price: ₹20*\n\n"
        "📜 *Terms*\n"
        "• One coupon per user\n"
        "• Non-refundable\n"
        "• Manual verification\n\n"
        "Agree to continue?"
    )

    kb = [
        [InlineKeyboardButton("✅ I Agree", callback_data="agree")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)

    if q.data == "agree":
        await context.bot.send_photo(
            chat_id=int(uid),
            photo=open("upi_qr.png", "rb"),
            caption="💸 Pay ₹20\nAfter payment click below"
        )

        kb = [[InlineKeyboardButton("✅ I've Paid", callback_data="paid")]]
        await context.bot.send_message(int(uid), "Confirm after payment", reply_markup=InlineKeyboardMarkup(kb))

    elif q.data == "paid":
        pending = load(PENDING_FILE, {})
        pending[uid] = q.from_user.username or q.from_user.first_name
        save(PENDING_FILE, pending)

        await q.edit_message_text("⏳ Payment sent for verification.\nPlease wait.")

        kb = [[
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{uid}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{uid}")
        ]]

        await context.bot.send_message(
            ADMIN_ID,
            f"💰 Payment claim\nUser ID: {uid}",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif q.data.startswith("approve_"):
        uid = q.data.split("_")[1]
        stock = load_stock()
        used = load(USED_FILE, {})
        pending = load(PENDING_FILE, {})

        if not stock:
            await q.edit_message_text("❌ No stock")
            return

        coupon = stock.pop(0)
        used[uid] = coupon

        save_stock(stock)
        save(USED_FILE, used)
        pending.pop(uid, None)
        save(PENDING_FILE, pending)

        await context.bot.send_message(
            int(uid),
            f"🎉 Payment confirmed!\n\n🎟 Coupon:\n`{coupon}`",
            parse_mode="Markdown"
        )

        await q.edit_message_text("✅ Approved & coupon sent")

    elif q.data.startswith("reject_"):
        uid = q.data.split("_")[1]
        pending = load(PENDING_FILE, {})
        pending.pop(uid, None)
        save(PENDING_FILE, pending)

        await context.bot.send_message(
            int(uid),
            "❌ Payment not received. Please try again."
        )

        await q.edit_message_text("❌ Rejected")


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.run_polling()

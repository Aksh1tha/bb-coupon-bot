from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
import os

# 🔑 BOT TOKEN (Railway variable)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 👑 YOUR ADMIN ID
ADMIN_ID = 5877824106

# 📢 CHANNEL USERNAME
CHANNEL_USERNAME = "@ugcwaksh"

# 📦 STORAGE (resets if bot restarts)
STOCK = []            # coupon codes
USED_USERS = set()    # users who already got coupon
WAITING_USERS = set() # users waiting for stock


# ✅ CHECK CHANNEL JOIN
async def is_user_member(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# 🚀 START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # 🔒 FORCE CHANNEL JOIN
    if not await is_user_member(context.bot, user_id):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url="https://t.me/ugcwaksh")],
            [InlineKeyboardButton("✅ I've Joined", callback_data="check_join")]
        ]
        await update.message.reply_text(
            "🔒 To use this bot, you must join our channel first.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # 📜 TERMS & CONDITIONS
    text = (
        "💸 *MRP: ₹20*\n\n"
        "📜 *Terms & Conditions*\n\n"
        "• Applicable ONLY for BigBasket first-time users\n"
        "• One coupon per mobile number\n"
        "• Order within a few hours\n"
        "• ₹100 off on selected products\n"
        "• Coupons are unique & non-refundable\n"
        "• We are not responsible for cancelled orders\n"
        "• Payments cannot be reversed\n\n"
        "🔗 Applicable products:\n"
        "https://www.bigbasket.com/sh/f9c23\n\n"
        "*Do you agree?*"
    )

    keyboard = [
        [InlineKeyboardButton("✅ I Agree", callback_data="agree")],
        [InlineKeyboardButton("❌ Decline", callback_data="decline")]
    ]

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 🔁 CHECK JOIN BUTTON
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if await is_user_member(context.bot, query.from_user.id):
        await query.edit_message_text("✅ Thanks for joining! Send /start again.")
    else:
        await query.answer("❌ Please join the channel first.", show_alert=True)


# 🎯 BUTTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # ✅ AGREED
    if query.data == "agree":

        if not STOCK:
            WAITING_USERS.add(user_id)

            # 🔔 Notify admin
            await context.bot.send_message(
                ADMIN_ID,
                "⚠️ Stock is empty! Please add more coupons."
            )

            await query.edit_message_text(
                "❌ No stock available right now.\n\nYou will be notified once stock is added."
            )
            return

        # 💸 SEND QR
        await context.bot.send_photo(
            chat_id=user_id,
            photo=open("upi_qr.png", "rb"),
            caption="💸 Pay ₹20 using this UPI QR.\n\nAfter payment, click below 👇"
        )

        keyboard = [
            [InlineKeyboardButton("✅ I've Paid", callback_data="paid")]
        ]

        await context.bot.send_message(
            user_id,
            "Click after successful payment:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # 💰 PAYMENT CONFIRM
    elif query.data == "paid":

        if user_id in USED_USERS:
            await query.edit_message_text("❌ You already received a coupon.")
            return

        if not STOCK:
            await query.edit_message_text("❌ Stock empty. Please wait.")
            return

        coupon = STOCK.pop(0)
        USED_USERS.add(user_id)

        await query.edit_message_text(
            f"🎉 *Payment received!*\n\n🎟 *Your Coupon Code:*\n\n`{coupon}`",
            parse_mode="Markdown"
        )

    # ❌ DECLINE
    elif query.data == "decline":
        await query.edit_message_text("❌ You must agree to continue.")


# 🛠 ADMIN: ADD STOCK
async def add_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    coupons = context.args

    if not coupons:
        await update.message.reply_text("❌ Usage: /addstock CODE1 CODE2 CODE3")
        return

    STOCK.extend(coupons)
    await update.message.reply_text(f"✅ Added {len(coupons)} coupons.")

    # 🔔 Notify waiting users
    for user in WAITING_USERS:
        await context.bot.send_message(
            user,
            "✅ Coupons are available now! Send /start"
        )

    WAITING_USERS.clear()


# 🚀 APP SETUP
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addstock", add_stock))
app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
app.add_handler(CallbackQueryHandler(button_handler, pattern="agree|decline|paid"))

app.run_polling()

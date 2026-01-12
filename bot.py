from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

# 👇 Your channel username
CHANNEL_USERNAME = "@ugcwaksh"


# ✅ Check if user joined channel
async def is_user_member(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# 🚀 Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # 🔒 Force join channel
    if not await is_user_member(context.bot, user_id):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url="https://t.me/ugcwaksh")],
            [InlineKeyboardButton("✅ I've Joined", callback_data="check_join")]
        ]
        await update.message.reply_text(
            "🔒 To use this bot, you must join our channel first.\n\n"
            "After joining, click ✅ I've Joined",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # ✅ User joined → show Terms & Conditions
    text = (
        "MRP: ₹20\n\n"
        "📜 Terms & Conditions\n\n"
        "By continuing, you agree:\n\n"
        "• This offer is applicable ONLY for BigBasket first-time users "
        "who have never placed an order before.\n\n"
        "• You can order only once per mobile number.\n\n"
        "• We recommend placing the order within a few hours or within 1 day.\n\n"
        "• 💰 Each code gives ₹100 off on BigBasket on selected products.\n"
        "• 🔐 Codes are unique and non-refundable.\n"
        "• 🚫 Don’t share codes publicly.\n"
        "• 🧾 We’re not responsible for cancelled orders.\n"
        "• ⚠️ Some items may not be eligible for coupons.\n"
        "• 💸 Payments, once made, can't be reversed.\n\n"
        "• Applicable to these products only:\n"
        "https://www.bigbasket.com/sh/f9c23\n\n"
        "Do you agree?"
    )

    keyboard = [
        [InlineKeyboardButton("✅ I Agree", callback_data="agree")],
        [InlineKeyboardButton("❌ Decline", callback_data="decline")]
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# 🔁 Check Join button
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if await is_user_member(context.bot, user_id):
        await query.edit_message_text(
            "✅ Thanks for joining!\n\nSend /start again to continue."
        )
    else:
        await query.answer(
            "❌ Please join the channel first.",
            show_alert=True
        )


# 🎯 Agree / Decline handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "agree":
        await query.edit_message_text("✅ Great! Please proceed to payment.")
    elif query.data == "decline":
        await query.edit_message_text("❌ You must agree to continue.")


# 🚀 App setup
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
app.add_handler(CallbackQueryHandler(button_handler, pattern="agree|decline"))

app.run_polling()


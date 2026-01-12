from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "MRP: ₹20\n\n"
        "📜 Terms & Conditions\n\n"
        "• Only for BigBasket first-time users\n"
        "• One order per mobile number\n"
        "• Order within few hours\n\n"
        "💰 ₹100 off on selected products\n"
        "🔐 Codes are unique & non-refundable\n"
        "🚫 Don’t share codes publicly\n"
        "🧾 We’re not responsible for cancelled orders\n"
        "⚠️ Some items may not be eligible\n"
        "💸 Payments can’t be reversed\n\n"
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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "agree":
        await query.edit_message_text("✅ Great! Please proceed to payment.")
    else:
        await query.edit_message_text("❌ You must agree to continue.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()

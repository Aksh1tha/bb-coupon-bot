from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

accepted_users = set()

TERMS_TEXT = (
    "💸 *MRP: ₹20*\n\n"
    "📜 *Terms & Conditions*\n\n"
    "By continuing, you agree:\n\n"
    "• Applicable only for *BigBasket first-time users* (no previous orders).\n"
    "• *One order per mobile number*.\n"
    "• Recommended to order *within a few hours or within 1 day*.\n\n"
    "• 💰 Each code gives *₹100 OFF* on selected BigBasket products.\n"
    "• 🔐 Codes are *unique, single-use & non-refundable*.\n"
    "• 🚫 Do not share codes publicly.\n"
    "• 🧾 We are not responsible for cancelled orders.\n"
    "• ⚠️ Some items may not be eligible.\n"
    "• 💸 Payments once made cannot be reversed.\n\n"
    "📦 Applicable products:\n"
    "https://www.bigbasket.com/sh/f9c23\n\n"
    "*Do you agree?*"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ I Agree", callback_data="accept")],
        [InlineKeyboardButton("❌ Decline", callback_data="decline")]
    ]

    await update.message.reply_text(
        TERMS_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "accept":
        accepted_users.add(user_id)

        keyboard = [
            [InlineKeyboardButton("🛒 Buy Coupon", callback_data="buy")],
            [InlineKeyboardButton("💰 Price", callback_data="price")],
            [InlineKeyboardButton("🆘 Support", callback_data="support")]
        ]

        await query.edit_message_text(
            "✅ *Terms accepted!*\n\nWelcome to *BB Coupon Store* 💸\n\nChoose an option:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "decline":
        await query.edit_message_text(
            "❌ You must accept the Terms & Conditions to use this bot."
        )

    elif user_id not in accepted_users:
        await query.edit_message_text("⚠️ Please accept the Terms & Conditions first.")

    elif query.data == "price":
        await query.edit_message_text(
            "💰 *Price*\n\nBB Coupon: *₹20*",
            parse_mode="Markdown"
        )

    elif query.data == "support":
        await query.edit_message_text(
            "🆘 *Support*\n\nFor help, contact:\n@yourusername",
            parse_mode="Markdown"
        )

    elif query.data == "buy":
        await query.edit_message_text(
            "🛒 *Buy Coupon*\n\n"
            "Pay *₹20* to:\n"
            "`aksh@upi`\n\n"
            "After payment, send screenshot 📸",
            parse_mode="Markdown"
        )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()

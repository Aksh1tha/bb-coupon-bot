from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 123456789  # 🔴 PUT YOUR TELEGRAM ID HERE
CHANNEL_USERNAME = "@ugcwaksh"


# ---------- Helpers ----------
def load_coupons():
    if not os.path.exists("coupons.txt"):
        return []
    with open("coupons.txt", "r") as f:
        return [x.strip() for x in f if x.strip()]


def save_coupons(coupons):
    with open("coupons.txt", "w") as f:
        f.write("\n".join(coupons))


def mark_used(code):
    with open("used.txt", "a") as f:
        f.write(code + "\n")


async def is_user_member(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# ---------- Start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_user_member(context.bot, user_id):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url="https://t.me/ugcwaksh")],
            [InlineKeyboardButton("✅ I've Joined", callback_data="check_join")]
        ]
        await update.message.reply_text(
            "🔒 Please join our channel to use this bot.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    text = (
        "MRP: ₹20\n\n"
        "📜 Terms & Conditions\n\n"
        "• Only for BigBasket first-time users\n"
        "• One order per mobile number\n"
        "• Order within few hours\n"
        "• ₹100 off on selected products\n"
        "• Codes are unique & non-refundable\n"
        "• Payments can’t be reversed\n\n"
        "Do you agree?"
    )

    keyboard = [
        [InlineKeyboardButton("✅ I Agree", callback_data="agree")],
        [InlineKeyboardButton("❌ Decline", callback_data="decline")]
    ]

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# ---------- Join Check ----------
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if await is_user_member(context.bot, query.from_user.id):
        await query.edit_message_text("✅ Joined successfully. Send /start")
    else:
        await query.answer("❌ Join channel first", show_alert=True)


# ---------- Button Handler ----------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "agree":
        keyboard = [
            [InlineKeyboardButton("✅ I Have Paid", callback_data="paid")]
        ]
        await query.message.reply_photo(
            photo=open("upi_qr.png", "rb"),
            caption="💳 Scan QR & complete payment.\n\nAfter payment click ✅ I Have Paid",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "decline":
        await query.edit_message_text("❌ You must agree to continue.")

    elif query.data == "paid":
        user = query.from_user

        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Confirm Payment",
                    callback_data=f"confirm_{user.id}"
                )
            ]
        ]

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💰 PAYMENT REQUEST\n\nUser: @{user.username}\nID: {user.id}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await query.edit_message_text(
            "⏳ Payment pending admin confirmation.\nPlease wait."
        )


# ---------- Admin Confirms ----------
async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    user_id = int(query.data.split("_")[1])

    coupons = load_coupons()
    if not coupons:
        await query.edit_message_text("❌ No coupon stock left.")
        return

    code = coupons.pop(0)
    save_coupons(coupons)
    mark_used(code)

    await context.bot.send_message(
        chat_id=user_id,
        text=f"🎉 PAYMENT CONFIRMED!\n\nYour coupon code:\n\n`{code}`",
        parse_mode="Markdown"
    )

    await query.edit_message_text("✅ Coupon sent successfully.")


# ---------- App ----------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
app.add_handler(CallbackQueryHandler(button_handler, pattern="agree|decline|paid"))
app.add_handler(CallbackQueryHandler(confirm_payment, pattern="confirm_"))

app.run_polling()

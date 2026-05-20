from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext

ASK_NAME, ASK_PHONE, QUIZ = range(3)

ADMIN_ID = 7856514246  # O'zingizning Telegram ID'ingizni yozing
CHANNEL_USERNAME = "@Studentacademiy"

# Savollarni oldindan qo‘shib qo‘yish
quiz_questions = [
    {"question": "I ___ a student.", "options": ["am", "is", "are"], "answer": "am"},
    {"question": "She ___ my friend.", "options": ["am", "is", "are"], "answer": "is"},
    {"question": "This is a ___.", "options": ["cat", "run", "blue"], "answer": "cat"},
    {"question": "Apple is ___.", "options": ["blue", "red", "run"], "answer": "red"},
    {"question": "We ___ happy.", "options": ["am", "is", "are"], "answer": "are"},
    {"question": "24 + 16 − 10 = ___", "options": ["20", "30", "40", "50"], "answer": "30"},
    {"question": "5 × 6 − 8 = ___", "options": ["22", "24", "30", "38"], "answer": "22"},
    {"question": "72 ÷ 8 + 9 = ___", "options": ["15", "16", "18", "20"], "answer": "18"},
    {"question": "40 − (12 + 8) = ___", "options": ["10", "15", "20", "30"], "answer": "20"},
    {"question": "Agar 1 soatda 60 daqiqa bo‘lsa, 3 soatda qancha daqiqa bor?", "options": ["120", "150", "180", "240"], "answer": "180"},
]

user_data_store = {}

async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    # Kanal obunasini tekshirish
    member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
    if member.status in ["left", "kicked"]:
        await update.message.reply_text(f"Iltimos, {CHANNEL_USERNAME} kanaliga obuna bo‘ling!")
        return ConversationHandler.END

    await update.message.reply_text("Ism va familiyangizni kiriting:")
    return ASK_NAME

async def ask_name(update: Update, context: CallbackContext):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Telefon raqamingizni kiriting (+998...):")
    return ASK_PHONE

async def ask_phone(update: Update, context: CallbackContext):
    context.user_data["phone"] = update.message.text
    context.user_data["answers"] = []
    context.user_data["score"] = 0
    context.user_data["current_q"] = 0
    user_data_store[update.message.from_user.id] = context.user_data
    return await ask_question(update, context)

async def ask_question(update: Update, context: CallbackContext):
    idx = context.user_data["current_q"]
    if idx < len(quiz_questions):
        q = quiz_questions[idx]
        options_text = " | ".join(q["options"])
        await update.message.reply_text(f"Savol {idx+1}: {q['question']}\nVariantlar: {options_text}")
        return QUIZ
    else:
        # Test tugadi
        name = context.user_data["name"]
        phone = context.user_data["phone"]
        answers = context.user_data["answers"]
        score = context.user_data["score"]

        result_text = f"Ism: {name}\nTel: {phone}\nBall: {score}/{len(quiz_questions)}\nJavoblar: {answers}"
        await context.bot.send_message(chat_id=ADMIN_ID, text=result_text)
        await update.message.reply_text("Test tugadi! Rahmat.")
        return ConversationHandler.END

async def quiz_answer(update: Update, context: CallbackContext):
    answer = update.message.text.strip()
    idx = context.user_data["current_q"]
    q = quiz_questions[idx]

    context.user_data["answers"].append({q["question"]: answer})
    if answer.lower() == q["answer"].lower():
        context.user_data["score"] += 1

    context.user_data["current_q"] += 1
    return await ask_question(update, context)

async def list_users(update: Update, context: CallbackContext):
    if update.message.from_user.id == ADMIN_ID:
        text = "Foydalanuvchilar ro‘yxati:\n"
        for uid, data in user_data_store.items():
            text += f"{data['name']} - {data['phone']} - Ball: {data['score']}\n"
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("Siz admin emassiz.")

def main():
    app = Application.builder().token("8877829655:AAE28jMJk3LR550S3BsmKladh8IuSy9nLBc").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            QUIZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_answer)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("list_users", list_users))

    app.run_polling()

if __name__ == "__main__":
    main()

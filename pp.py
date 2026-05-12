import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ======================
# 🔧 CONFIG
# ======================
TOKEN = "8689733180:AAFmWh5icYB3aTN0HcXzWPBCLOTl5KucWt8"
CHANNEL_USERNAME = "@sasujegive"

# ======================
# 📦 DATABASE (FIXED)
# ======================
DATA_FILE = "users.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

users = data.get("users", {})
verified = set(data.get("verified", []))

# ======================
# 💰 COMMISSION RULE
# ======================
def earning(level):
    table = {
        1: 10,
        2: 9,
        3: 8,
        4: 7,
        5: 6,
        6: 5,
        7: 4,
        8: 3,
        9: 2,
        10: 1
    }
    return table.get(level, 1)

# ======================
# 🔗 GET UPLINE CHAIN
# ======================
def get_upline_chain(user_id, levels=10):
    chain = []
    current = users.get(user_id, {}).get("ref")

    for _ in range(levels):
        if not current or current not in users:
            break
        chain.append(current)
        current = users[current].get("ref")

    return chain

# ======================
# 💸 DISTRIBUTE INCOME (FIXED)
# ======================
async def notify_upline(new_user_id, context):

    chain = get_upline_chain(new_user_id, 10)

    for level, upline in enumerate(chain, start=1):

        if upline not in users:
            continue

        amount = earning(level)

        users[upline]["balance"] = users[upline].get("balance", 0) + amount

        msg = (
            "🎉 সুখবর!\n\n"
            "👤 নতুন ইউজার join করেছে\n"
            f"📊 লেভেল: {level}\n"
            f"💰 পেয়েছেন: {amount}৳\n\n"
            "💡 ব্যালেন্স আপডেট হয়েছে"
        )

        try:
            await context.bot.send_message(chat_id=upline, text=msg)
        except:
            pass

    # 💾 SAVE ONCE ONLY (FIX)
    save_data({"users": users, "verified": list(verified)})

# ======================
# 🏠 START (FIXED REF SYSTEM)
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.message.from_user.id)

    if user_id not in users:
        users[user_id] = {
            "ref": None,
            "balance": 0,
            "downline": []
        }

    # 🔗 REF SYSTEM FIXED
    if context.args:
        ref = context.args[0]

        users[user_id]["ref"] = ref

        if ref in users:
            if user_id not in users[ref]["downline"]:
                users[ref]["downline"].append(user_id)

        save_data({"users": users, "verified": list(verified)})

        # 🔥 IMPORTANT TRIGGER FIX
        await notify_upline(user_id, context)

    keyboard = [
        ["🔗 চ্যানেল জয়েন", "✅ ভেরিফাই"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "👋 স্বাগতম!\n🔒 আগে ভেরিফাই করুন",
        reply_markup=reply_markup
    )

# ======================
# 📩 HANDLER (FULL FIXED)
# ======================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    user_id = str(update.message.from_user.id)

    # 🔗 JOIN CHANNEL
    if text == "🔗 চ্যানেল জয়েন":

        await update.message.reply_text(
            f"https://t.me/{CHANNEL_USERNAME.replace('@','')}"
        )

    # ✅ VERIFY
    elif text == "✅ ভেরিফাই":

        try:
            member = await context.bot.get_chat_member(
                CHANNEL_USERNAME,
                user_id
            )

            if member.status in ["member", "administrator", "creator"]:

                verified.add(user_id)

                # 💾 SAVE VERIFIED
                save_data({
                    "users": users,
                    "verified": list(verified)
                })

                keyboard = [
                    ["👥 ডাউনলাইন", "💰 ব্যালেন্স"],
                    ["🔗 রেফার লিঙ্ক", "💸 উইথড্র"]
                ]

                reply_markup = ReplyKeyboardMarkup(
                    keyboard,
                    resize_keyboard=True
                )

                await update.message.reply_text(
                    "🎉 ভেরিফাই সফল!\n\n🔓 সব ফিচার আনলক 🚀",
                    reply_markup=reply_markup
                )

            else:
                await update.message.reply_text(
                    "❌ আগে চ্যানেল জয়েন করুন!"
                )

        except:
            await update.message.reply_text(
                "⚠️ বটকে চ্যানেলের Admin করুন!"
            )

    # 👥 DOWNLINE
    elif text == "👥 ডাউনলাইন":

        if user_id not in verified:
            return await update.message.reply_text(
                "🔒 আগে ভেরিফাই করুন!"
            )

        # ======================
        # 🔍 GENERATION COUNT
        # ======================
        gens = {i: 0 for i in range(1, 11)}

        def count_downline(uid, level):

            if level > 10:
                return

            downlines = users.get(uid, {}).get("downline", [])

            gens[level] += len(downlines)

            for d in downlines:
                count_downline(d, level + 1)

        count_downline(user_id, 1)

        # ======================
        # 📊 TOTALS
        # ======================
        total_users = sum(gens.values())

        balance = users.get(user_id, {}).get(
            "balance",
            0
        )

        # ======================
        # 📝 MESSAGE
        # ======================
        msg = (
            "📊 ডাউনলাইন রিপোর্ট (১০ জেনারেশন)\n\n"
            f"👥 মোট রেফার: {total_users}\n"
            f"💰 মোট ব্যালেন্স: {balance}৳\n\n"
        )

        for i in range(1, 11):

            users_count = gens[i]

            amount = earning(i)

            income = users_count * amount

            msg += (
                f"🔹 {i} নং জেনারেশন\n"
                f"👥 ইউজার: {users_count}\n"
                f"💵 কমিশন: {amount}৳\n"
                f"💰 ইনকাম: {income}৳\n\n"
            )

        await update.message.reply_text(msg)

    # 💰 BALANCE
    elif text == "💰 ব্যালেন্স":

        if user_id not in verified:
            return await update.message.reply_text(
                "🔒 আগে ভেরিফাই করুন!"
            )

        balance = users.get(user_id, {}).get(
            "balance",
            0
        )

        await update.message.reply_text(
            f"💰 আপনার ব্যালেন্স:\n\n{balance}৳"
        )

    # 🔗 REFERRAL
    elif text == "🔗 রেফার লিঙ্ক":

        if user_id not in verified:
            return await update.message.reply_text(
                "🔒 আগে ভেরিফাই করুন!"
            )

        bot_username = (
            await context.bot.get_me()
        ).username

        link = (
            f"https://t.me/{bot_username}"
            f"?start={user_id}"
        )

        await update.message.reply_text(
            "🔗 আপনার রেফার লিঙ্ক:\n\n"
            f"{link}\n\n"
            "💰 প্রতি রেফারে ১০৳ পাবেন\n"
            "👥 ডাউনলাইন কমিশনও পাবেন 🚀"
        )

    # 💸 WITHDRAW
    elif text == "💸 উইথড্র":

        if user_id not in verified:
            return await update.message.reply_text(
                "🔒 আগে ভেরিফাই করুন!"
            )

        balance = users.get(user_id, {}).get(
            "balance",
            0
        )

        if balance < 1000:

            await update.message.reply_text(
                "❌ মিনিমাম ১০০০৳ লাগবে!\n\n"
                f"💰 বর্তমান ব্যালেন্স: {balance}৳"
            )

        else:

            await update.message.reply_text(
                "✅ উইথড্র রিকোয়েস্ট পাঠানো হয়েছে!"
            )

# ======================
# ▶️ RUN BOT
# ======================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling(drop_pending_updates=True)

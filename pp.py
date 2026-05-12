import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "YOUR_TOKEN"
CHANNEL = "@sasujegive"
FILE = "users.json"

# ======================
# DB
# ======================
def load():
    try:
        return json.load(open(FILE))
    except:
        return {"users": {}, "verified": []}

def save(d):
    json.dump(d, open(FILE, "w"))

db = load()
users = db["users"]
verified = set(db["verified"])

# ======================
# COMMISSION
# ======================
def earn(lv):
    return max(1, 11 - lv)

# ======================
# UPLINE
# ======================
def chain(uid, limit=10):
    res = []
    cur = users.get(uid, {}).get("ref")
    for _ in range(limit):
        if not cur or cur not in users:
            break
        res.append(cur)
        cur = users[cur].get("ref")
    return res

# ======================
# DISTRIBUTE
# ======================
async def reward(uid, ctx):
    for i, u in enumerate(chain(uid), 1):
        users.setdefault(u, {}).setdefault("balance", 0)
        users[u]["balance"] += earn(i)
        try:
            await ctx.bot.send_message(u, f"🎉 Level {i} +{earn(i)}৳")
        except:
            pass
    save({"users": users, "verified": list(verified)})

# ======================
# START
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)

    users.setdefault(uid, {"ref": None, "balance": 0, "down": []})

    if context.args:
        ref = context.args[0]
        users[uid]["ref"] = ref
        save({"users": users, "verified": list(verified)})
        await reward(uid, context)

    kb = [["🔗 Join", "✅ Verify"]]
    await update.message.reply_text("Welcome", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

# ======================
# HANDLER
# ======================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    text = update.message.text

    if text == "🔗 Join":
        await update.message.reply_text(f"https://t.me/{CHANNEL.replace('@','')}")
        return

    if text == "✅ Verify":
        verified.add(uid)
        save({"users": users, "verified": list(verified)})
        await update.message.reply_text("Verified ✔️")
        return

    if text == "💰 Balance":
        await update.message.reply_text(str(users.get(uid, {}).get("balance", 0)))

# ======================
# RUN
# ======================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle))

    app.run_polling()

if __name__ == "__main__":
    main()

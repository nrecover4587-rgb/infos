"""
TELEGRAM INFO BOT - Single File Version
Features: 2-Channel Force Subscribe | Advanced Admin Panel | perfect API Integration
Developer: @sexypym | Heroku Ready
"""

import os
import logging
import aiohttp
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

# ============ CONFIGURATION ============
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8876043411:AAHB2ghNBF6usbVOk8SZeq4WaRdR2aWJ61o")
ADMIN_IDS = list(map(int, os.environ.get("ADMIN_IDS", "7113972959").split(",")))

# OSINT API Configuration
OSINT_API_KEY = os.environ.get("OSINT_API_KEY", "ROLEX")
OSINT_API_URL = os.environ.get("OSINT_API_URL", "https://rootx-osint.in/")

# Channel 1 Configuration
FORCE_CHANNEL_1_ID = int(os.environ.get("FORCE_CHANNEL_1_ID", "-1003920248424"))
FORCE_CHANNEL_1_LINK = os.environ.get("FORCE_CHANNEL_1_LINK", "https://t.me/hangamaupdate")

# Channel 2 Configuration
FORCE_CHANNEL_2_ID = int(os.environ.get("FORCE_CHANNEL_2_ID", "-1003630527469"))
FORCE_CHANNEL_2_LINK = os.environ.get("FORCE_CHANNEL_2_LINK", "https://t.me/mistubots")

# Heroku Webhook
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://your-app-name.herokuapp.com")
PORT = int(os.environ.get("PORT", 8443))

# ============ INITIALIZATION ============
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ============ FORCE SUBSCRIBE CHECK ============
async def check_missing_channels(user_id: int):
    missing = []

    # Channel 1
    try:
        status1 = await bot.get_chat_member(
            chat_id=FORCE_CHANNEL_1_ID,
            user_id=user_id
        )

        if status1.status in ["left", "kicked"]:
            missing.append(("1", FORCE_CHANNEL_1_LINK))

    except Exception:
        missing.append(("1", FORCE_CHANNEL_1_LINK))

    # Channel 2
    try:
        status2 = await bot.get_chat_member(
            chat_id=FORCE_CHANNEL_2_ID,
            user_id=user_id
        )

        if status2.status in ["left", "kicked"]:
            missing.append(("2", FORCE_CHANNEL_2_LINK))

    except Exception:
        missing.append(("2", FORCE_CHANNEL_2_LINK))

    return missing

# ============ FORCE SUBSCRIBE MIDDLEWARE ============
@dp.message()
async def force_sub_middleware(message: Message):
    user_id = message.from_user.id
    missing = await check_missing_channels(user_id)

    if missing:
        buttons = []

        for num, link in missing:
            buttons.append([
                InlineKeyboardButton(
                    text=f"✅ Join Channel {num}",
                    url=link
                )
            ])

        buttons.append([
            InlineKeyboardButton(
                text="🔄 Verify",
                callback_data="check_sub"
            )
        ])

        await message.answer(
            f"⚠️ Access Restricted ⚠️\n\n"
            f"Please join {len(missing)} channel(s) first.\n\n"
            f"After joining click Verify.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=buttons
            )
        )
        return

    await process_command(message)

# ============ COMMAND PROCESSOR ============
async def process_command(message: Message):
    text = message.text

    if not text:
        return

    if text.startswith("/start"):
        await cmd_start(message)

    elif text.startswith("/help"):
        await cmd_help(message)

    elif text.startswith("/id"):
        await cmd_id(message)

    elif text.startswith("/info"):
        await cmd_info(message)

    elif text.startswith("/search"):
        await cmd_search(message)

    elif text.startswith("/admin") and message.from_user.id in ADMIN_IDS:
        await admin_panel(message)

    elif text.startswith("/checkuser") and message.from_user.id in ADMIN_IDS:
        await check_user(message)

# ============ OSINT LOOKUP ============
async def osint_lookup(mobile_number: str):
    try:
        async with aiohttp.ClientSession() as session:

            params = {
                "type": "num",
                "key": OSINT_API_KEY,
                "query": mobile_number
            }

            async with session.get(OSINT_API_URL, params=params) as response:

                if response.status == 200:
                    data = await response.json()
                    return data

                return None

    except Exception as e:
        logging.error(f"OSINT API Error: {e}")
        return None

# ============ RESULT FORMAT ============
def format_osint_result(data):

    if not data or len(data) == 0:
        return "❌ No results found."

    result = "🔍 OSINT SEARCH RESULT 🔍\n\n"

    result += f"📱 Mobile: {data[0].get('MOBILE', 'N/A')}\n"
    result += f"👤 Name: {data[0].get('NAME', 'N/A')}\n"
    result += f"👨 Father Name: {data[0].get('fname', 'N/A')}\n"
    result += f"🆔 ID: {data[0].get('id', 'N/A')}\n"

    raw_address = data[0].get('ADDRESS', 'N/A')

    if '!' in raw_address:
        address_parts = raw_address.replace('!', ' ').strip()
        result += f"📍 Address: {address_parts}\n"
    else:
        result += f"📍 Address: {raw_address}\n"

    result += f"📡 Circle: {data[0].get('circle', 'N/A')}\n"

    alt_num = data[0].get('alt', 'N/A')

    if alt_num != 'N/A':
        result += f"🔄 Alternate: {alt_num}\n"

    result += "\n⚠️ Use responsibly."

    return result

# ============ START ============
async def cmd_start(message: Message):

    await message.answer(
        f"👋 Welcome {message.from_user.full_name}!\n\n"
        f"🔍 OSINT Info Bot\n\n"
        f"/search [number]\n"
        f"/id\n"
        f"/info\n"
        f"/help\n\n"
        f"Example:\n"
        f"/search 7811017125"
    )

# ============ HELP ============
async def cmd_help(message: Message):

    await message.answer(
        "📖 Help Menu\n\n"
        "/start\n"
        "/search [number]\n"
        "/id\n"
        "/info\n"
        "/help\n"
    )

# ============ ID ============
async def cmd_id(message: Message):

    await message.answer(
        f"🆔 User ID: {message.from_user.id}"
    )

# ============ INFO ============
async def cmd_info(message: Message):

    await message.answer(
        "🤖 Bot Information\n\n"
        "Version: 2.0\n"
        "Framework: aiogram 3.x\n"
        "Platform: Heroku"
    )

# ============ SEARCH ============
async def cmd_search(message: Message):

    args = message.text.split(maxsplit=1)

    if len(args) < 2:

        await message.answer(
            "Usage:\n/search 9876543210"
        )
        return

    mobile_number = args[1].strip()

    if not mobile_number.isdigit() or len(mobile_number) < 10:

        await message.answer(
            "❌ Invalid mobile number."
        )
        return

    searching_msg = await message.answer(
        f"🔍 Searching {mobile_number}..."
    )

    result = await osint_lookup(mobile_number)

    if result:

        formatted_result = format_osint_result(result)

        await searching_msg.edit_text(
            formatted_result
        )

    else:

        await searching_msg.edit_text(
            "❌ Search failed."
        )

# ============ VERIFY ============
@dp.callback_query(F.data == "check_sub")
async def callback_check(callback: CallbackQuery):

    missing = await check_missing_channels(callback.from_user.id)

    if not missing:

        await callback.message.edit_text(
            "✅ Verification Successful!"
        )

    else:

        await callback.answer(
            f"Please join {len(missing)} channel(s).",
            show_alert=True
        )

# ============ ADMIN PANEL ============
class BroadcastState(StatesGroup):
    waiting_for_message = State()

async def admin_panel(message: Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Statistics",
                    callback_data="admin_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Bot Status",
                    callback_data="admin_status"
                )
            ]
        ]
    )

    await message.answer(
        "🔐 Admin Control Panel",
        reply_markup=keyboard
    )

# ============ ADMIN CALLBACK ============
@dp.callback_query(F.data.startswith("admin_"))
async def admin_actions(callback: CallbackQuery):

    if callback.from_user.id not in ADMIN_IDS:

        await callback.answer(
            "❌ Unauthorized",
            show_alert=True
        )
        return

    action = callback.data.split("_")[1]

    if action == "stats":

        await callback.message.answer(
            "📊 Bot Statistics\n\n"
            "OSINT API Connected"
        )

    elif action == "status":

        await callback.message.answer(
            "✅ Bot Running\n\n"
            f"Webhook: {WEBHOOK_URL}"
        )

    await callback.answer()

# ============ CHECK USER ============
async def check_user(message: Message):

    if not message.reply_to_message:

        await message.answer(
            "Reply to a user with /checkuser"
        )
        return

    user = message.reply_to_message.from_user

    await message.answer(
        f"👤 User Info\n\n"
        f"ID: {user.id}\n"
        f"Name: {user.full_name}\n"
        f"Username: @{user.username}"
    )

# ============ STARTUP ============
async def on_startup(app):

    await bot.set_webhook(
        f"{WEBHOOK_URL}/webhook"
    )

    print(f"✅ Webhook set: {WEBHOOK_URL}/webhook")
    print(f"🤖 Bot running on port {PORT}")

# ============ SHUTDOWN ============
async def on_shutdown(app):

    await bot.delete_webhook()
    await bot.session.close()

    print("🛑 Bot shutdown")

# ============ MAIN ============
def main():

    app = web.Application()

    # FIXED WEBHOOK ROUTE
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    ).register(
        app,
        path="/webhook"
    )

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(
        app,
        host="0.0.0.0",
        port=PORT
    )

# ============ RUN ============
if __name__ == "__main__":
    main()

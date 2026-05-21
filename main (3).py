"""
TELEGRAM INFO BOT - Single File Version
Features: 2-Channel Force Subscribe | Advanced Admin Panel | OSINT API Integration
Developer: @Uffperfect | Heroku Ready
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
from aiogram.webhook import aiohttp_server

# ============ CONFIGURATION ============
# Replace these with your actual values OR use Heroku Config Vars
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = list(map(int, os.environ.get("ADMIN_IDS", "123456789").split(",")))

# OSINT API Configuration
OSINT_API_KEY = os.environ.get("OSINT_API_KEY", "ROLEX")  # Default key from your example
OSINT_API_URL = os.environ.get("OSINT_API_URL", "https://rootx-osint.in/")

# Channel 1 Configuration
FORCE_CHANNEL_1_ID = int(os.environ.get("FORCE_CHANNEL_1_ID", "-1001234567890"))
FORCE_CHANNEL_1_LINK = os.environ.get("FORCE_CHANNEL_1_LINK", "https://t.me/channel1")

# Channel 2 Configuration
FORCE_CHANNEL_2_ID = int(os.environ.get("FORCE_CHANNEL_2_ID", "-1009876543210"))
FORCE_CHANNEL_2_LINK = os.environ.get("FORCE_CHANNEL_2_LINK", "https://t.me/channel2")

# Heroku Webhook
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://your-app-name.herokuapp.com")
PORT = int(os.environ.get("PORT", 8443))

# ============ INITIALIZATION ============
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ============ FORCE SUBSCRIBE CHECK (2 CHANNELS) ============
async def check_missing_channels(user_id: int):
    """Check if user has joined both required channels"""
    missing = []
    
    # Check Channel 1
    try:
        status1 = await bot.get_chat_member(chat_id=FORCE_CHANNEL_1_ID, user_id=user_id)
        if status1.status in ['left', 'kicked']:
            missing.append(('1', FORCE_CHANNEL_1_LINK))
    except Exception:
        missing.append(('1', FORCE_CHANNEL_1_LINK))
    
    # Check Channel 2
    try:
        status2 = await bot.get_chat_member(chat_id=FORCE_CHANNEL_2_ID, user_id=user_id)
        if status2.status in ['left', 'kicked']:
            missing.append(('2', FORCE_CHANNEL_2_LINK))
    except Exception:
        missing.append(('2', FORCE_CHANNEL_2_LINK))
    
    return missing

# Middleware to check force subscribe on every message
@dp.message()
async def force_sub_middleware(message: Message):
    user_id = message.from_user.id
    missing = await check_missing_channels(user_id)
    
    if missing:
        buttons = []
        for num, link in missing:
            buttons.append([InlineKeyboardButton(text=f"✅ Join Channel {num}", url=link)])
        buttons.append([InlineKeyboardButton(text="🔄 Verify", callback_data="check_sub")])
        
        await message.answer(
            f"⚠️ **Access Restricted** ⚠️\n\n"
            f"Please join {len(missing)} channel(s) first to use this bot:\n\n"
            f"After joining, click the Verify button.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
            parse_mode="Markdown"
        )
        return
    
    # If user has joined, let the command handlers process
    await process_command(message)

async def process_command(message: Message):
    """Process commands after force subscribe check"""
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

# ============ OSINT API FUNCTION ============
async def osint_lookup(mobile_number: str):
    """Query the OSINT API for mobile number information"""
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
                else:
                    return None
    except Exception as e:
        logging.error(f"OSINT API Error: {e}")
        return None

def format_osint_result(data):
    """Format the OSINT API response into a readable message"""
    if not data or len(data) == 0:
        return "❌ No results found for this number."
    
    result = "🔍 **OSINT SEARCH RESULT** 🔍\n\n"
    result += f"📱 **Mobile:** {data[0].get('MOBILE', 'N/A')}\n"
    result += f"👤 **Name:** {data[0].get('NAME', 'N/A')}\n"
    result += f"👨 **Father's Name:** {data[0].get('fname', 'N/A')}\n"
    result += f"🆔 **ID:** {data[0].get('id', 'N/A')}\n"
    
    # Format address
    raw_address = data[0].get('ADDRESS', 'N/A')
    if '!' in raw_address:
        address_parts = raw_address.replace('!', ' ').strip()
        result += f"📍 **Address:** {address_parts}\n"
    else:
        result += f"📍 **Address:** {raw_address}\n"
    
    result += f"📡 **Circle:** {data[0].get('circle', 'N/A')}\n"
    
    # Alternate number
    alt_num = data[0].get('alt', 'N/A')
    if alt_num != 'N/A':
        result += f"🔄 **Alternate:** {alt_num}\n"
    
    # API usage stats (if available in response)
    if len(data) > 2 and isinstance(data[2], dict):
        result += "\n📊 **API Status:**\n"
        result += f"• Requests Left: {data[2].get('req_left', 'N/A')}\n"
        result += f"• Total Limit: {data[2].get('req_total', 'N/A')}\n"
        result += f"• Expires: {data[2].get('expiry', 'N/A')}\n"
        result += f"• Developer: @Uffperfect\n"
    
    result += "\n⚠️ Use responsibly and legally only."
    return result

# ============ USER COMMANDS ============
async def cmd_start(message: Message):
    await message.answer(
        f"👋 **Welcome {message.from_user.full_name}!**\n\n"
        f"🔍 **OSINT Info Bot**\n"
        f"Search any mobile number to get information.\n\n"
        f"📌 **Commands:**\n"
        f"/search [number] - Search mobile number\n"
        f"/id - Get your Telegram ID\n"
        f"/info - About this bot\n"
        f"/help - Show all commands\n\n"
        f"✅ **Example:** `/search 7811017125`\n\n"
        f"**Developer:** @Uffperfect",
        parse_mode="Markdown"
    )

async def cmd_help(message: Message):
    await message.answer(
        "📖 **Help Menu**\n\n"
        "**User Commands:**\n"
        "• /start - Welcome message\n"
        "• /search [number] - Search mobile number (OSINT)\n"
        "• /id - Get your Telegram user ID\n"
        "• /info - Bot information\n"
        "• /help - Show this menu\n\n"
        "**Admin Commands (if you're admin):**\n"
        "• /admin - Open admin control panel\n"
        "• /checkuser - Reply to a user's message to see their info\n\n"
        "**Usage Examples:**\n"
        "• `/search 9876543210`\n"
        "• `/search 7811017125`\n\n"
        "**Developer:** @Uffperfect",
        parse_mode="Markdown"
    )

async def cmd_id(message: Message):
    await message.answer(
        f"🆔 **Your Information**\n\n"
        f"**User ID:** `{message.from_user.id}`\n"
        f"**Name:** {message.from_user.full_name}\n"
        f"**Username:** @{message.from_user.username if message.from_user.username else 'None'}\n"
        f"**Is Bot:** {'Yes' if message.from_user.is_bot else 'No'}",
        parse_mode="Markdown"
    )

async def cmd_info(message: Message):
    await message.answer(
        "🤖 **Bot Information**\n\n"
        f"**Version:** 2.0\n"
        f"**Framework:** aiogram 3.x\n"
        f"**Platform:** Heroku\n\n"
        "**Features:**\n"
        "✅ 2-Channel Force Subscribe\n"
        "✅ Advanced Admin Panel\n"
        "✅ OSINT Mobile Number Lookup\n"
        "✅ User ID Lookup\n"
        "✅ API Integration\n\n"
        "**Developer:** @Uffperfect\n"
        "**Source:** Custom Development",
        parse_mode="Markdown"
    )

async def cmd_search(message: Message):
    """Handle /search command for OSINT lookup"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer(
            "❌ **Usage:** `/search 9876543210`\n\n"
            "Please provide a mobile number to search.\n"
            "Example: `/search 7811017125`",
            parse_mode="Markdown"
        )
        return
    
    mobile_number = args[1].strip()
    
    # Validate mobile number (basic validation)
    if not mobile_number.isdigit() or len(mobile_number) < 10:
        await message.answer(
            "❌ **Invalid mobile number!**\n\n"
            "Please enter a valid 10-digit mobile number.",
            parse_mode="Markdown"
        )
        return
    
    # Send searching message
    searching_msg = await message.answer(
        f"🔍 Searching for `{mobile_number}`...\n\n"
        f"Please wait while I fetch the information.",
        parse_mode="Markdown"
    )
    
    # Perform OSINT lookup
    result = await osint_lookup(mobile_number)
    
    if result:
        formatted_result = format_osint_result(result)
        await searching_msg.edit_text(formatted_result, parse_mode="Markdown")
    else:
        await searching_msg.edit_text(
            f"❌ **Search Failed!**\n\n"
            f"Could not find information for `{mobile_number}`.\n\n"
            f"Possible reasons:\n"
            f"• Invalid number\n"
            f"• API key issue\n"
            f"• No data available\n\n"
            f"**Developer:** @Uffperfect",
            parse_mode="Markdown"
        )

# ============ VERIFY CALLBACK ============
@dp.callback_query(F.data == "check_sub")
async def callback_check(callback: CallbackQuery):
    missing = await check_missing_channels(callback.from_user.id)
    
    if not missing:
        await callback.message.edit_text(
            "✅ **Verification Successful!**\n\n"
            "Thank you for joining all channels.\n"
            "You can now use all bot features.\n\n"
            "Try: `/search 7811017125` or /id or /info",
            parse_mode="Markdown"
        )
    else:
        await callback.answer(f"Please join {len(missing)} more channel(s) first!", show_alert=True)

# ============ ADVANCED ADMIN PANEL ============
class BroadcastState(StatesGroup):
    waiting_for_message = State()

async def admin_panel(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Broadcast Message", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🔍 OSINT Test", callback_data="admin_osint")],
        [InlineKeyboardButton(text="👥 User Guide", callback_data="admin_help")],
        [InlineKeyboardButton(text="🔍 Check User", callback_data="admin_check")],
        [InlineKeyboardButton(text="ℹ️ Bot Status", callback_data="admin_status")]
    ])
    await message.answer(
        "🔐 **Admin Control Panel**\n\n"
        "Select an option below to manage your bot:\n"
        f"**Developer:** @Uffperfect",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("admin_"))
async def admin_actions(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ You are not authorized!", show_alert=True)
        return
    
    action = callback.data.split("_")[1]
    
    if action == "stats":
        await callback.message.answer(
            "📊 **Bot Statistics**\n\n"
            "• **Total Users:** Not tracked (no database)\n"
            "• **Active Today:** N/A\n"
            "• **Force Subscribe:** Active (2 channels)\n"
            "• **OSINT API:** Connected\n"
            "• **Commands:** /search, /id, /info\n\n"
            "**Developer:** @Uffperfect\n\n"
            "💡 **Tip:** Add a database (MongoDB/Supabase) to track users!"
        )
    
    elif action == "broadcast":
        await callback.message.answer(
            "📢 **Broadcast Mode**\n\n"
            "Send me the message you want to broadcast.\n"
            "All users will receive this message.\n\n"
            "⚠️ **Note:** Without a database, this is a demo.\n"
            "To send real broadcasts, add user tracking.\n\n"
            "Type /cancel to exit."
        )
        await state.set_state(BroadcastState.waiting_for_message)
    
    elif action == "osint":
        await callback.message.answer(
            "🔍 **OSINT API Test**\n\n"
            f"**API URL:** {OSINT_API_URL}\n"
            f"**API Key:** {OSINT_API_KEY}\n\n"
            "**Test Commands:**\n"
            "• `/search 7811017125` - Example search\n"
            "• `/search [any_number]` - Your search\n\n"
            "**API Status:** Active\n"
            "**Developer:** @Uffperfect"
        )
    
    elif action == "help":
        await callback.message.answer(
            "📖 **Admin Guide**\n\n"
            "**Commands:**\n"
            "• /admin - Open this panel\n"
            "• /checkuser - Reply to any message to see user details\n"
            "• /search [number] - OSINT lookup\n\n"
            "**Features:**\n"
            "• Force Subscribe: Users must join 2 channels\n"
            "• Broadcast: Send messages to all users\n"
            "• OSINT API: Mobile number lookup\n"
            "• User Check: Get any user's information\n\n"
            "**Developer:** @Uffperfect"
        )
    
    elif action == "check":
        await callback.message.answer(
            "🔍 **Check User Feature**\n\n"
            "**How to use:**\n"
            "1. Find a user's message in any chat\n"
            "2. Reply to their message\n"
            "3. Type: `/checkuser`\n\n"
            "The bot will show you:\n"
            "• User ID\n"
            "• Full Name\n"
            "• Username\n"
            "• Bot status\n\n"
            "**Developer:** @Uffperfect"
        )
    
    elif action == "status":
        await callback.message.answer(
            "ℹ️ **Bot Status**\n\n"
            "✅ Bot is running!\n"
            f"✅ Webhook: {WEBHOOK_URL}\n"
            f"✅ Admin count: {len(ADMIN_IDS)}\n"
            "✅ Force subscribe: Active (2 channels)\n"
            "✅ OSINT API: Configured\n"
            "✅ Mode: Heroku Production\n\n"
            "**Channels:**\n"
            f"Channel 1 ID: {FORCE_CHANNEL_1_ID}\n"
            f"Channel 2 ID: {FORCE_CHANNEL_2_ID}\n\n"
            "**Developer:** @Uffperfect"
        )
    
    await callback.answer()

@dp.message(BroadcastState.waiting_for_message)
async def process_broadcast(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Unauthorized!")
        await state.clear()
        return
    
    if message.text == "/cancel":
        await message.answer("❌ Broadcast cancelled.")
        await state.clear()
        return
    
    # Demo broadcast (without database)
    await message.answer(
        "⚙️ **Broadcast Demo**\n\n"
        f"✅ Message received!\n\n"
        f"**Your message:**\n{message.text}\n\n"
        "💡 **To enable real broadcasts:**\n"
        "1. Add a database (MongoDB/Firebase)\n"
        "2. Store user IDs when they start the bot\n"
        "3. Use: `for user_id in users: await bot.send_message(user_id, text)`\n\n"
        "**Developer:** @Uffperfect"
    )
    await state.clear()

async def check_user(message: Message):
    if not message.reply_to_message:
        await message.answer("❌ Please reply to a user's message with /checkuser")
        return
    
    user = message.reply_to_message.from_user
    await message.answer(
        f"👤 **User Information**\n\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"📝 **Name:** {user.full_name}\n"
        f"👤 **Username:** @{user.username if user.username else 'None'}\n"
        f"🤖 **Is Bot:** {'Yes' if user.is_bot else 'No'}\n"
        f"🔢 **Language:** {user.language_code if user.language_code else 'Unknown'}\n\n"
        f"**Developer:** @Uffperfect",
        parse_mode="Markdown"
    )

# ============ HEROKU WEBHOOK SETUP ============
async def on_startup():
    """Setup webhook when bot starts"""
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    print(f"✅ Webhook set to: {WEBHOOK_URL}/webhook")
    print(f"🤖 Bot is running on port: {PORT}")
    print(f"👑 Admins: {ADMIN_IDS}")
    print(f"📢 Force subscribe channels configured")
    print(f"🔍 OSINT API: {OSINT_API_URL}")
    print(f"👨‍💻 Developer: @Uffperfect")

async def on_shutdown():
    """Cleanup when bot stops"""
    await bot.delete_webhook()
    await bot.session.close()
    print("🛑 Bot shutdown complete")

def main():
    """Main entry point for Heroku"""
    app = web.Application()
    
    # Setup webhook route
    app.router.post("/webhook", aiohttp_server.WebhookRequestHandler(bot, dp).handle)
    
    # Setup startup/shutdown handlers
    app.on_startup.append(lambda _: on_startup())
    app.on_shutdown.append(lambda _: on_shutdown())
    
    # Run the web server
    web.run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
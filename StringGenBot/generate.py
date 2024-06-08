from pyrogram.types import Message
from telethon import TelegramClient
from pyrogram import Client, filters
from pyrogram1 import Client as Client1
from asyncio.exceptions import TimeoutError
from telethon.sessions import StringSession
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from pyrogram1.errors import (
    ApiIdInvalid as ApiIdInvalid1,
    PhoneNumberInvalid as PhoneNumberInvalid1,
    PhoneCodeInvalid as PhoneCodeInvalid1,
    PhoneCodeExpired as PhoneCodeExpired1,
    SessionPasswordNeeded as SessionPasswordNeeded1,
    PasswordHashInvalid as PasswordHashInvalid1
)
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)

import config



ask_ques = "⋄ اذا كنت تريد تنصيب سورس ميوزك\nفأختار بايروجرام\n⋄ واذا كنت تريد تنصيب تيلثون\nفأختار تيرمكس\n⋄ اذا كنت تريد تنصيب سورس علي اخر اصدار\nتحديثات فأختار بايروجرام V2\n⋄ يوجد استخرجات جلسات لي البوتات :"
buttons_ques = [
    [
        InlineKeyboardButton("‹ بايروجرام ›", callback_data="pyrogram1"),        
        InlineKeyboardButton("‹ بايروجرام V2 ›", callback_data="pyrogram"),
    ],
    [
        InlineKeyboardButton("‹ تيلثون ›", callback_data="telethon"),
    ],
    [
        InlineKeyboardButton("‹ بايروجرام بوت ›", callback_data="pyrogram_bot"),
        InlineKeyboardButton("‹ تيلثون بوت ›", callback_data="telethon_bot"),
    ],
]

gen_button = [
    [
        InlineKeyboardButton(text="📥↫اطغط لبدا استخراج كود↬📥", callback_data="generate")
    ]
]




@Client.on_message(filters.private & ~filters.forwarded & filters.command(["generate", "gen", "string", "str"]))
async def main(_, msg):
    await msg.reply(ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques))


async def generate_session(bot: Client, msg: Message, telethon=False, old_pyro: bool = False, is_bot: bool = False):
    if telethon:
        ty = "Telethon"
    else:
        ty = "Pyrogram"
        if not old_pyro:
            ty += " v2"
    if is_bot:
        ty += " Bot"
    await msg.reply(f"⋄ تم بدأ انشاء جلسه **{ty}** 🔍")
    user_id = msg.chat.id
    api_id_msg = await bot.ask(user_id, "🎮 حسنا قم الان بأرسال ايبي ايدي حسابك\n\n- للتخطي ارسل /skip", filters=filters.text)
    if await cancelled(api_id_msg):
        return
    if api_id_msg.text == "/skip":
        api_id = config.API_ID
        api_hash = config.API_HASH
    else:
        try:
            api_id = int(api_id_msg.text)
        except ValueError:
            await api_id_msg.reply("⋄ خطا يجب ان يكون الايبي ايدي عدداً صحيح\n↢ يرجي المحاوله مره اخري", quote=True, reply_markup=InlineKeyboardMarkup(gen_button))
            return
        api_hash_msg = await bot.ask(user_id, "💈 حسنا قم الان بأرسال ايبي هاش حسابك", filters=filters.text)
        if await cancelled(api_hash_msg):
            return
        api_hash = api_hash_msg.text
    if not is_bot:
        t = "**⋄ الان قم بأرسال رقم الهاتف مع رمز الدوله\n↢ `مثال `+20123456789**"
    else:
        t = "⋄ ارسل الان توكن بوتك من @BotFather"
    phone_number_msg = await bot.ask(user_id, t, filters=filters.text)
    if await cancelled(phone_number_msg):
        return
    phone_number = phone_number_msg.text
    if not is_bot:
        await msg.reply("**⋄ يتم الان ارسال رمز التحقق انتظر...**")
    else:
        await msg.reply("**⋄ جاري الان محاوله التسجيل الاجباري عبر التوكن...**")
    if telethon and is_bot:
        client = TelegramClient(StringSession(), api_id, api_hash)
    elif telethon:
        client = TelegramClient(StringSession(), api_id, api_hash)
    elif is_bot:
        client = Client(name="bot", api_id=api_id, api_hash=api_hash, bot_token=phone_number, in_memory=True)
    elif old_pyro:
        client = Client1(":memory:", api_id=api_id, api_hash=api_hash)
    else:
        client = Client(name="user", api_id=api_id, api_hash=api_hash, in_memory=True)
    await client.connect()
    try:
        code = None
        if not is_bot:
            if telethon:
                code = await client.send_code_request(phone_number)
            else:
                code = await client.send_code(phone_number)
    except (ApiIdInvalid, ApiIdInvalidError, ApiIdInvalid1):
        await msg.reply("⋄ تأكـد من ايبيهات حسابك لان بها خطأ \n سوي /start مره اخري", reply_markup=InlineKeyboardMarkup(gen_button))
        return
    except (PhoneNumberInvalid, PhoneNumberInvalidError, PhoneNumberInvalid1):
        await msg.reply("⋄ رقم الهاتف غير مسجل بالتليجرام من الاصل \n اذا انت متاكد من الرقم قم بارسال /start مره اخري", reply_markup=InlineKeyboardMarkup(gen_button))
        return
    try:
        phone_code_msg = None
        if not is_bot:
            phone_code_msg = await bot.ask(user_id, "**تحقق من الرسائل في تيليجرام وارسل رمز التحقق**\n\nقم بإرساله بالشكل التالي :\n`1234` => 1 2 3 4\nاترك مسافة بين كل رقم", filters=filters.text, timeout=600)
            if await cancelled(phone_code_msg):
                return
    except TimeoutError:
        await msg.reply("⋄ انتهي مهله المسموح بها للانتظار 5 دقائق استخرج مره اخري /start", reply_markup=InlineKeyboardMarkup(gen_button))
        return
    if not is_bot:
        phone_code = phone_code_msg.text.replace(" ", "")
        try:
            if telethon:
                await client.sign_in(phone_number, phone_code, password=None)
            else:
                await client.sign_in(phone_number, code.phone_code_hash, phone_code)
        except (PhoneCodeInvalid, PhoneCodeInvalidError, PhoneCodeInvalid1):
            await msg.reply("⋄ كود التحقق الذي ارسلته غير صحيح حاول مره اخري /start ...", reply_markup=InlineKeyboardMarkup(gen_button))
            return
        except (PhoneCodeExpired, PhoneCodeExpiredError, PhoneCodeExpired1):
            await msg.reply("⋄ لقد انتهي صلاحية كود التحقق الذي أرسلته\n↢ يرجى المحاولة مرة أخرى...", reply_markup=InlineKeyboardMarkup(gen_button))
            return
        except (SessionPasswordNeeded, SessionPasswordNeededError, SessionPasswordNeeded1):
            try:
                two_step_msg = await bot.ask(user_id, "⋄ أرسل الأن ارسل التحقق بخوطين للمتابعه", filters=filters.text, timeout=300)
            except TimeoutError:
                await msg.reply("⋄ انتهي وقت الجلسه 5 دقائق يرجى اعاده استخراج الجلسه من البدايه /start", reply_markup=InlineKeyboardMarkup(gen_button))
                return
            try:
                password = two_step_msg.text
                if telethon:
                    await client.sign_in(password=password)
                else:
                    await client.check_password(password=password)
                if await cancelled(api_id_msg):
                    return
            except (PasswordHashInvalid, PasswordHashInvalidError, PasswordHashInvalid1):
                await two_step_msg.reply("⋄ كلمه مرور حسابك غير صحيحه\n↢ يرجي المحاولة مره اخري /start", quote=True, reply_markup=InlineKeyboardMarkup(gen_button))
                return
    else:
        if telethon:
            await client.start(bot_token=phone_number)
        else:
            await client.sign_in_bot(phone_number)
    if telethon:
        string_session = client.session.save()
    else:
        string_session = await client.export_session_string()
    text = f"⋄ تم استخراج جلسة\n\n`{string_session}`\n\n**↢ استخراج بواسطة : @al11ibot\n↢ ملحوظه : حافظ عليها ممكن حد يخترقكك بيها\nاشترك بالحب @WX_PM ♥️"
    try:
        if not is_bot:
            await client.send_message("me", text)
            await bot.send_message(msg.chat.id, text)
        else:
            await bot.send_message(msg.chat.id, text)
    except KeyError:
        pass
    await client.disconnect()
    await bot.send_message(msg.chat.id, "↢ تم استخراج الجلسه بنجاح ‹  › 🔍 من فضلك تفحص الرسايل المحفوظه بحسابك \nJoin @WX_PM 💈".format("telethon" if telethon else "pyrogram"))


async def cancelled(msg):
    if "/cancel" in msg.text:
        await msg.reply("⋄ تم إلغاء عملية إنشاء الجلسة", quote=True, reply_markup=InlineKeyboardMarkup(gen_button))
        return True
    elif "/restart" in msg.text:
        await msg.reply("⋄ تم بنجاح إعادة تشغيل هذا الروبوت", quote=True, reply_markup=InlineKeyboardMarkup(gen_button))
        return True
    elif "/skip" in msg.text:
        return False
    elif msg.text.startswith("/"):  # Bot Commands
        await msg.reply("⋄ تم إلغاء عملية إنشاء الجلسة", quote=True)
        return True
    else:
        return False
        

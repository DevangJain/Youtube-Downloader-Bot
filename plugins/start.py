import asyncio

from pyrogram import Client, filters
from core.creds import Credentials
from core.database import Database
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, UsernameNotOccupied, ChatAdminRequired, PeerIdInvalid


async def send_msg(user_id, message):
    try:
        await message.forward(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"


## --- Start Handler --- ##
@Client.on_message(Filters.command(["start"]), group=-2)
async def start(client, message):
## --- Users Adder --- ##
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
    ## --- Force Sub --- ##
    update_channel = Credentials.UPDATES_CHANNEL
    if update_channel:
        try:
            user = await client.get_chat_member(update_channel, message.from_user.id)
            if user.status == "kicked":
               await client.send_message(
                   chat_id=message.chat.id,
                   text="Sorry Sir, You are Banned!\nNow Your Can't Use Me. Contact my [Support Group](https://t.me/damienhelp).",
                   parse_mode="markdown",
                   disable_web_page_preview=True
               )
               return
        except UserNotParticipant:
            await client.send_message(
                chat_id=message.chat.id,
                text="**Please Join My Updates Channel to use this Bot!**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("💬 Join Updates Channel", url=f"https://t.me/{update_channel}")
                        ]
                    ]
                ),
                parse_mode="markdown"
            )
            return
        except Exception:
            await client.send_message(
                chat_id=message.chat.id,
                text="Something went Wrong. Contact my [Support Group](https://t.me/damienhelp).",
                parse_mode="markdown",
                disable_web_page_preview=True
            )
            return
    await message.reply_text(
    f"Hi, {message.from_user.mention}.\nI am Telegram to telegra.ph image uploader bot.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="💬 Updates Channel", url="https://t.me/DamienSoukara"),
                    InlineKeyboardButton(text="🗣 Support Group", url="https://t.me/damienhelp")
                ],
                [
                    InlineKeyboardButton("🤖 : About", callback_data="about")
                ]
            ]
        ),
        parse_mode="html",
        disable_web_page_preview=True
    )


@Client.on_message(filters.private & filters.command("status") & filters.user(Credentials.ADMIN))
async def sts(bot, cmd):
    total_users = await db.total_users_count()
    await cmd.reply_text(text=f"**Total Users in DB:** `{total_users}`", parse_mode="Markdown")



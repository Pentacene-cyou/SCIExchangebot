""" sciexchangebot utils """
from os import remove
from asyncio import sleep, create_subprocess_shell
from asyncio.subprocess import PIPE
from sciexchangebot import bot

async def execute(command, pass_error=True):
    """ Executes command and returns output, with the option of enabling stderr. """
    executor = await create_subprocess_shell(
        command,
        stdout=PIPE,
        stderr=PIPE
    )

    stdout, stderr = await executor.communicate()
    if pass_error:
        result = str(stdout.decode().strip()) \
                 + str(stderr.decode().strip())
    else:
        result = str(stdout.decode().strip())
    return result

async def attach_log(plaintext, chat_id, file_name, reply_id=None, caption=None):
    """ Attach plaintext as logs. """
    file = open(file_name, "w+")
    file.write(plaintext)
    file.close()
    await bot.send_file(
        chat_id,
        file_name,
        reply_to=reply_id,
        caption=caption
    )
    remove(file_name)

async def send_log(plaintext, chat_id: int) -> None:
    """ Send plaintext as text """
    await bot.send_message(
        chat_id,
        plaintext
    )

async def notification(context, message: str, time: int = 5, delete_original: bool = False) -> None:
    """ Send Notification and delete it after some seconds """
    notification_message = await context.reply(message)
    if delete_original:
        await context.delete()
    await sleep(time)
    await notification_message.delete()
    return

def process_link(chat_id: int, message_id: int) -> str:
    if chat_id < 0:
        return f'https://t.me/c/{(chat_id + 1000000000000) * (-1)}/{message_id}'
    elif chat_id > 0:
        return f'https://t.me/c/{chat_id}/{message_id}'
    else:
        return ''

def cid(chat_id: int) -> int:
    return ((chat_id + 1000000000000) * (-1))

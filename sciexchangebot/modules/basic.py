""" sciexchangebot basic functions """
from datetime import datetime
from sciexchangebot import log
from ..listener import listener

@listener(incoming=True, outgoing=True, command="ping")
async def ping(context):
    """ Calculates latency between PagerMaid and Telegram. """
    start = datetime.now()
    pong = await context.reply("Hi!")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await pong.edit(f"Hi! | {duration} ms")
    await context.delete()

@listener(incoming=True, outgoing=True, command="restart")
async def restart(context):
    """ To re-execute PagerMaid. """
    if not context.text[0].isalpha():
        await log("sciexchangebot restart")
        await context.client.disconnect()

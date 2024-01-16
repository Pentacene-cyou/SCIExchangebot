""" sciexchangebot module start """
from asyncio import TimeoutError
from telethon import Button
from telethon.utils import pack_bot_file_id
from sciexchangebot import config, logger
from .get_recent_10_unhelped import get_recent_unhelped_url
from ..listener import listener, process_link
from ..database import is_in_blacklist, select, update

CHANNEL_ID = int(config['telegram']['channel_id'])
CHANNEL_NAME = config['telegram']['channel_name']
DOCUMENT_GROUP_ID = int(config['telegram']['document_group_id'])

@listener(outgoing=True, incoming=True, command="start")
async def start(context):
    if context.chat_id < 0:
        await context.delete()
        return
    if is_in_blacklist(context.sender.id):
        await context.reply(
            ('I am sorry to hear that you have been banned from using this bot.\n' 
             'Please reach out to @Pentacene for further communication and assistance.'))
        return
    if len(context.parameter) == 0:
        await context.reply(
            ('Hello, please first follow @SCIExchange. \n'
             'Enter the DOI number of the article you would like assistance with.\n\n'
             "Due to Sci-hub's resumption of uploading new papers, you can try sending the paper request to @scihubot " 
             'or attempt to use the official website https://sci-hub.se/ to find this paper.'))
        logger.info(f'[START] USER_ID: {context.sender.id}')
    else:
        msg_id = int(context.parameter[0])
        logger.info(f'[FILE] [INIT] USER_ID:MSG_ID =  {context.sender.id}:{context.parameter[0]}')
        async with context.client.conversation(context.chat_id) as conv:
            await conv.send_message('Please send the file you wish to transfer.')
            try:
                response = await conv.get_response(timeout=600)
                user_id = select('user_id', 'msg_id', msg_id)
                if response.document:
                    file_id = pack_bot_file_id(response.document)
                    document = await context.client.send_file(
                        DOCUMENT_GROUP_ID,
                        caption=f'[{msg_id}](https://t.me/{CHANNEL_NAME}/{msg_id})',
                        file=file_id)
                    document_id = document.id
                    await context.client.send_file(
                        user_id,
                        caption=f'[{msg_id}](https://t.me/{CHANNEL_NAME}/{msg_id})',
                        file=file_id)
                    logger.info(f'[FILE] [CHECK] USER_ID:MSG_ID:DOCUMENT_ID =  {user_id}:{msg_id}:{document_id}')

                    bot_msg = await context.client.send_message(
                        user_id,
                        'The literature you were looking for has received a response! Is this the one you were referring to?',
                        buttons=[Button.inline('Yes', b'YES'), Button.inline('No', b'NO')])
                    
                    bot_msg_id = bot_msg.id
                    if not (update('document_id', document_id, 'msg_id', msg_id) and update('bot_msg_id', bot_msg_id, 'msg_id', msg_id)):
                        logger.error(f'[DATABASE] [LOG_UPDATE_FR_MSG_ID] ("document_id", {document_id}, {msg_id})')
                        await response.reply('DATABASE ERROR! PLEASE reach out to @Pentacene')

                    await response.reply((
                        f'Thank you for providing the document! The seeker has been notified.\n'
                        f'{get_recent_unhelped_url()}'))
                    logger.info(f'[FILE] [SUCCESS] USER_ID:MSG_ID:DOCUMENT_ID = {user_id}:{msg_id}:{document_id}')

                    await context.client.edit_message(
                        CHANNEL_ID,
                        msg_id,
                        link_preview=False,
                        buttons=[
                            Button.inline(
                                '🤔UnderReview',
                                b'UnderReview'),
                            Button.url(
                                'Click2view',
                                process_link(DOCUMENT_GROUP_ID, document_id))])
                    if not update('b_status', 2, 'msg_id', msg_id):
                        logger.error(f'[DATABASE] [LOG_UPDATE_B_STATUS] ({document_id}, {msg_id})')
                        await response.reply('DATABASE ERROR! PLEASE reach out to @Pentacene')
                else:
                    await response.reply(
                        'It seems like what you sent is not a file. Please click the button again to resend.')
                    logger.info(f'[FILE] [NOTDOC] USER_ID:MSG_ID = {user_id}:{msg_id}')
            except TimeoutError:
                await conv.send_message(
                    ('You have exceeded the time limit, and the conversation has been closed.'
                     'If you need to send a file, please enter from the original entrance and send it again.'))
                logger.info(f'[FILE] [TIMEOUT] USER:WID = {context.sender.id}:{context.parameter[0]}')

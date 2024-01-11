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
            (f'你因为 {is_in_blacklist(context.sender.id)} 被禁止使用此服务。详情请联系 @Pentacene\n'
             f'You have been banned from this service. Please contact @Pentacene for more details.'))
        return
    if len(context.parameter) == 0:
        await context.reply(
            ('您好, 请您先关注 @SCIExchange \n'
             '请输入您想要求助的文章doi号或文章网址:\n\n'
             '由于 [Sci-hub已经恢复上传新论文](https://t.me/SCIExchange/234) 您可以试试将论文请求发送给 @scihubot '
             '或尝试使用官方网站 https://sci-hub.se/ 查找这篇论文\n\n'
             'Please first subscribe @SCIExchange for next step.\n'
             'Please send URL from publisher or DOI links.\n'
             'You may send requests to @scihubot or check https://sci-hub.se/{url} '
             'for your requests since SCI-HUB back to work.'))
        logger.info(f'[START] USER_ID: {context.sender.id}')
    else:
        msg_id = int(context.parameter[0])
        logger.info(f'[FILE] [INIT] USER_ID:MSG_ID =  {context.sender.id}:{context.parameter[0]}')
        async with context.client.conversation(context.chat_id) as conv:
            await conv.send_message('请发送您要传输的文件\nPlease send your files')
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
                        ('您要找的文献已经有人回复啦! 请问是这个嘛?\n'
                            'Someone reply your request. Is this the right one?'),
                        buttons=[Button.inline('是的Yes', b'YES'), Button.inline('不是No', b'NO')])
                    
                    bot_msg_id = bot_msg.id
                    if not (update('document_id', document_id, 'msg_id', msg_id) and update('bot_msg_id', bot_msg_id, 'msg_id', msg_id)):
                        logger.error(f'[DATABASE] [LOG_UPDATE_FR_MSG_ID] ("document_id", {document_id}, {msg_id})')
                        await response.reply('数据库错误,请联系 @Pentacene')

                    await response.reply((
                        f'感谢您提供文件! 已经通知寻找者~\n'
                        f'Thanks for the files. Already sent notification to requester.\n'
                        f'{get_recent_unhelped_url()}'))
                    logger.info(f'[FILE] [SUCCESS] USER_ID:MSG_ID:DOCUMENT_ID = {user_id}:{msg_id}:{document_id}')

                    await context.client.edit_message(
                        CHANNEL_ID,
                        msg_id,
                        link_preview=False,
                        buttons=[
                            Button.inline(
                                '🤔审核中Checking',
                                b'UnderReview'),
                            Button.url(
                                '点我查看Click2View',
                                process_link(DOCUMENT_GROUP_ID, document_id))])
                    if not update('b_status', 2, 'msg_id', msg_id):
                        logger.error(f'[DATABASE] [LOG_UPDATE_B_STATUS] ({document_id}, {msg_id})')
                        await response.reply('数据库错误,请联系 @Pentacene')
                else:
                    await response.reply(
                        ('您发送的好像不是一个文件,请您重新点击按钮发送~\n'
                         'It seems like you did not sent a file. Please click send button on channel again.'))
                    logger.info(f'[FILE] [NOTDOC] USER_ID:MSG_ID = {user_id}:{msg_id}')
            except TimeoutError:
                await conv.send_message(
                    ('您已超时,对话已关闭.如您需要发送文件请从原入口进入后再发送.\n'
                     'Timeout due to the limit of Telegram. Please click send button on channel again.'))
                logger.info(f'[FILE] [TIMEOUT] USER:WID = {context.sender.id}:{context.parameter[0]}')

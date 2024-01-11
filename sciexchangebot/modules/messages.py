""" sciexchangebot modules messages """
from telethon import Button
from telethon.tl.functions.channels import LeaveChannelRequest
from sciexchangebot import config, logger
from ..listener import listener, process_link
from ..database import log, select, is_in_blacklist
from .doi_resolver import resolve_doi, is_doi

CHANNEL_ID = int(config['telegram']['channel_id'])
CHANNEL_NAME = config['telegram']['channel_name']
DOCUMENT_GROUP_ID = int(config['telegram']['document_group_id'])
ADMIN_GROUP_ID = int(config['telegram']['admin_group'])
BOT_NAME = config['telegram']['name']

def is_legal_url(msg: str) -> bool:
    if msg.startswith("https://"):
        return True
    elif msg.startswith("http://"):
        return True
    elif msg.startswith("doi.org"):
        return True
    else:
        return False

async def request2channel(context, url: str, is_doi: bool = True) -> None:
    if is_doi:
        msg = await context.client.send_message(
            DOCUMENT_GROUP_ID,
            f'https://doi.org/{url}',
            link_preview=False)
    else:
        msg = await context.client.send_message(
            DOCUMENT_GROUP_ID,
            context.text,
            link_preview=False)
    await msg.edit(
        link_preview=False,
        buttons=[
            Button.inline(f'😭未找到notFound', b'notFound'),
            Button.url('如果您有请点我iHaveThis', f"https://t.me/{BOT_NAME}?start={msg.id}")])
    if not log(msg.chat_id, msg.id, context.sender.id, str(url)):
        logger.error(f'[DATABASE] [LOG] {msg.chat_id}, {msg.id}, {context.sender.id}, {str(url)}')
    await context.reply(
        (f'您的请求已被发送到这里,请查看~ \n'
         f'The request has been sent here. Please check.\n'
         f'由于 [Sci-hub已经恢复上传新论文](https://t.me/SCIExchange/234) '
         f'您可以试试将论文请求发送给 @scihubot 或尝试使用官方网站 https://sci-hub.se/{url} 查找这篇论文\n'
         f'You may send requests to @scihubot or check https://sci-hub.se/{url} for your requests since SCI-HUB back to work.'),
        buttons=[Button.url('您的发布信息UrPost', f'https://t.me/{CHANNEL_NAME}/{msg.id}')])
    logger.info(f'[SENDREQUEST] USER_ID:MSG = {context.sender.id}:{context.text}')
    return

async def request_already_exist(context, msg_id: int) -> None:
    document_id = select('document_id', 'msg_id', msg_id)
    text = '你要找的这篇内容已经有人问过啦~\nYour requests is already in database.\n'
    b_status = select('b_status', 'msg_id', msg_id)
    logger.info(f'[ALREADYASKED] USER_ID:DOCUMENT_ID:B_STATUS = {context.sender.id}:{document_id}:{b_status}')
    if b_status == 0:
        await context.reply(
            f'{text}可惜没有人回答哦. 你能帮帮忙嘛?\nBut nobody sent files.',
            buttons=[Button.url('如果您有请点我iHaveThis', f"https://t.me/{BOT_NAME}?start={msg_id}")])
        logger.info(f'[ALREADYASKED] [NODOC] USER_ID:DOCUMENT_ID:B_STATUS = {context.sender.id}:{document_id}:{b_status}')
    else:
        await context.reply(
            f'{text}在这里哦👇\nIs right here👇',
            buttons=[Button.url('点我查看Click2View', process_link(DOCUMENT_GROUP_ID, document_id))])
        logger.info(f'[ALREADYASKED] [SENT] USER_ID:DOCUMENT_ID:B_STATUS = {context.sender.id}:{document_id}:{b_status}')

@listener(incoming=True)
async def log_message(context):
    if context.chat_id < 0:
        if context.chat_id == CHANNEL_ID:
            return
        if context.chat_id == DOCUMENT_GROUP_ID:
            return
        if context.chat_id == ADMIN_GROUP_ID:
            return
        await context.client(LeaveChannelRequest(context.chat_id))
        logger.info(f'[LEAVE] ID {context.chat_id}')

    if is_in_blacklist(context.sender.id):
        await context.reply(
            (f'你因为 {is_in_blacklist(context.sender.id)} 被禁止使用此服务。详情请联系 @Pentacene\n'
             f'You have been banned from this service. Please contact @Pentacene for more details.'))
        return

    if context.video or context.gif or context.photo or context.document or context.grouped_id or context.sticker:
        return
    elif context.text:
        if context.is_group or context.is_channel:
            return
        else:
            if context.text.startswith('/'):
                return
            if is_legal_url(context.text) or is_doi(context.text):
                doi = await resolve_doi(context.text)
                msg_id = select('msg_id', 'doi', doi)
                if not msg_id:
                    if doi is None:
                        await request2channel(context, context.text, False)
                    else:
                        await request2channel(context, doi)
                    # await context.reply(f'')
                else:
                    await request_already_exist(context, msg_id)
            elif is_doi(context.text):
                doi = context.text
                msg_id = select('msg_id', 'doi', doi)
                if not msg_id:
                    await request2channel(context, doi)
                else:
                    await request_already_exist(context, msg_id)
            else:
                await context.reply(
                    ('您发布的消息可能不含有链接信息,请您发布所需要的论文出版社网址或doi网址\n'
                     '例如: `https://doi.org/` \n'
                     'The message you sent may have no URLs, please send doi process_link '
                     'or the process_link from publisher. Such as `https://doi.org/` '))
                logger.info(f'[SENDREQUEST] [NOTURL] UID:MSG = {context.sender.id}:{context.text}')
    else:
        return

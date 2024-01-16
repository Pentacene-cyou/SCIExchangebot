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

async def request2channel(context, doi: str) -> None:
    msg = await context.client.send_message(
        CHANNEL_ID,
        f'https://doi.org/{doi}',
        link_preview=False)
    await msg.edit(
        link_preview=False,
        buttons=[
            Button.inline(f'😭notFound', b'notFound'),
            Button.url('iHaveThisArticle', f"https://t.me/{BOT_NAME}?start={msg.id}")])
    if not log(msg.chat_id, msg.id, context.sender.id, str(doi)):
        logger.error(f'[DATABASE] [LOG] {msg.chat_id}, {msg.id}, {context.sender.id}, {str(doi)}')
    await context.reply(
        (f'Your request has been sent here. Please click the button below to view. \n'
         f"Due to Sci-hub's resumption of uploading new papers, you can try sending the paper request to @scihubot " 
         f'or attempt to use the official website https://sci-hub.se/{doi} to find this paper.'),
        buttons=[Button.url('UrPostedInfo', f'https://t.me/{CHANNEL_NAME}/{msg.id}')])
    return

async def request_already_exist(context, msg_id: int) -> None:
    document_id = select('document_id', 'msg_id', msg_id)
    text = 'The content you are looking for has already been inquired by someone else.\n'
    b_status = select('b_status', 'msg_id', msg_id)
    logger.info(f'[ALREADYASKED] USER_ID:DOCUMENT_ID:B_STATUS = {context.sender.id}:{document_id}:{b_status}')
    if b_status == 0:
        await context.reply(
            f'{text}Unfortunately, no one has answered. Can you help?',
            buttons=[Button.url('iHaveThisArticle', f"https://t.me/{BOT_NAME}?start={msg_id}")])
        logger.info(f'[ALREADYASKED] [NODOC] USER_ID:DOCUMENT_ID:B_STATUS = {context.sender.id}:{document_id}:{b_status}')
    else:
        await context.reply(
            f'{text}Is right here👇',
            buttons=[Button.url('Click2view', process_link(DOCUMENT_GROUP_ID, document_id))])
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
        logger.info(f'[MESSAGE] [LEAVE] ID = {context.chat_id}')
        return

    if is_in_blacklist(context.sender.id):
        await context.reply(
            ('I am sorry to hear that you have been banned from using this bot.\n' 
             'Please reach out to @Pentacene for further communication and assistance.'))
        logger.info(f'[MESSAGE] [BAN] uid = {context.sender.id}')
        return

    if context.video or context.gif or context.photo or context.document or context.grouped_id or context.sticker:
        return
    elif context.text:
        if context.text.startswith('/'):
            return
        if is_doi(context.text):
            doi = resolve_doi(context.text)
            msg_id = select('msg_id', 'doi', doi)
            if msg_id == 0:
                await request2channel(context, doi)
                logger.info(f'[MESSAGE] [REQUEST2CHANNEL] UID:DOI = {context.sender.id}:{doi}')
            else:
                await request_already_exist(context, msg_id)
                logger.info(f'[MESSAGE] [ALREADY_EXIST] UID:MID = {context.sender.id}:{msg_id}')
        else:
            await context.reply(
                ('Please provide the DOI number for the article you need to send.\n' 
                 'For example, `10.1002/adma.202400001` '))
            logger.info(f'[MESSAGE] [NOT_DOI] UID:MSG = {context.sender.id}:{context.text}')
    else:
        return

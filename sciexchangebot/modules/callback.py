""" sciexchangebot module button clicked """
import re
from telethon import events, Button
from telethon.errors.rpcerrorlist import UserIsBlockedError
from sciexchangebot import bot, config, logger
from ..database import is_in_blacklist, select, update, add_blacklist
from ..listener import process_link
from .get_recent_10_unhelped import get_recent_unhelped_url

CHECK_GROUP_ID = config['check_group_id']
CHANNEL_ID = int(config['telegram']['channel_id'])
CHANNEL_NAME = config['telegram']['channel_name']
DOCUMENT_GROUP_ID = int(config['telegram']['document_group_id'])
BOT_NAME = config['telegram']['name']

@bot.on(events.CallbackQuery)
async def handler(event):
    msg_id = event.original_update.msg_id
    user_id = event.original_update.user_id
    # if user in blacklist
    if is_in_blacklist(user_id):
        await event.answer(
            ('I am sorry to hear that you have been banned from using this bot.\n' 
             'Please reach out to @Pentacene for further communication and assistance.'))
        logger.info(f'[CALLBACK] [blacklist] UID:MID = {user_id}:{msg_id}')
        return
    # if 😭未找到notFound has been clicked
    if event.data == b'notFound':
        # by check group, AD
        if user_id in CHECK_GROUP_ID:
            await it_is_ad(event, select('user_id', 'msg_id', msg_id))
            logger.info(f'[CALLBACK] [DELETE] UID:MID:EVENT = {user_id}:{msg_id}:{event.original_update}')
        else:
            await event.answer('Can you help?')
    # if 🤔审核中Checking has been clicked
    elif event.data == b'UnderReview':
        # by check group, review by check group
        if user_id in CHECK_GROUP_ID:
            event.answer('Review by Admins')
            await review_request(event, msg_id)
            logger.info(f'[CALLBACK] [REVIEW] {msg_id} by {user_id}')
    # if 😊已找到Found has been clicked
    elif event.data == b'Found':
        if user_id == 1012414645:
            event.answer(select('user_id', 'msg_id', msg_id))
    # if Yes has been clicked
    elif event.data == b'YES':
        bot_msg_id = msg_id
        msg_id = select('msg_id', 'bot_msg_id', bot_msg_id)
        document_id = select('document_id', 'bot_msg_id', bot_msg_id)
        await event.answer('Congratulations on finding the article you were looking for!')
        await event.edit(
            f'Congratulations on finding the article you were looking for!\n{get_recent_unhelped_url()}',
            buttons=Button.url(
                'Archieves',
                process_link(DOCUMENT_GROUP_ID, document_id)))
        if not update('b_status', 1, 'bot_msg_id', bot_msg_id):
            await event.answer('DATABASE ERROR!')
            logger.error(f'[CALLBACK] [DATABASE] [LOG_UPDATE_FR_BOT_MSG_ID] ("b_status", 1, {bot_msg_id})')
        await change_status(event, msg_id, document_id)
        logger.info(f'[CALLBACK] [CHECK] [CURRECT] USER_ID:MSG_ID:DOCUMENT_ID = {user_id}:{msg_id}:{document_id}')
    # if No has been clicked
    elif event.data == b'NO':
        bot_msg_id = msg_id
        await event.answer("Let's wait and see again then.")
        await event.edit((
            f"The literature you were looking for has received a response." 
            f"Unfortunately, it is not what you were hoping for.\n"
            f'{get_recent_unhelped_url()}'))
        if not update('document_id', 0, 'bot_msg_id', bot_msg_id):
            await event.answer('DATABASE ERROR!')
            logger.error(f'[CALLBACK] [DATABASE] [LOG_UPDATE_FR_BOT_MSG_ID] ("document_id", 0, {bot_msg_id})')
        logger.info(f'[CALLBACK] [CHECK] [INCURRECT] USER_ID = {user_id}')
        await change_status(event, msg_id, 0, False)
    elif event.data == b'Review_accept':
        msg = await event.get_message()
        text = msg.text
        msg_id = re.search(f"https://t.me/{CHANNEL_NAME}/([0-9]+)", text).group(1)
        msg_id = int(msg_id)
        await review(event, msg_id, is_accept=True)
        logger.info(f'[CALLBACK] [REVIEW] [ACCEPT] {msg_id} by {user_id}')
    elif event.data == b'Review_reject':
        msg = await event.get_message()
        text = msg.text
        msg_id = re.search(f"https://t.me/{CHANNEL_NAME}/([0-9]+)", text).group(1)
        msg_id = int(msg_id)
        await review(event, msg_id, is_accept=False)
        logger.info(f'[CALLBACK] [REVIEW] [REJECT] {msg_id} by {user_id}')
    elif event.data == b'banYes':
        if user_id in CHECK_GROUP_ID:
            ban_id = select('user_id', 'msg_id', msg_id)
            await event.client.edit_permissions(CHANNEL_ID, ban_id, view_messages=False)
            await event.client.edit_permissions(DOCUMENT_GROUP_ID, ban_id, view_messages=False)
            add_blacklist(ban_id, 'STOP BOT')
            logger.info(f'[CALLBACK] [BAN] [Button] USER_ID = {ban_id}')
            event.answer('BURN IT ALL!')
        else:
            event.answer("DON'T CLICK")
    elif event.data == b'banNo':
        event.answer('SO KINDNESS')

async def change_status(event, msg_id: int, document_id: int, is_found: bool = True) -> None:
    if is_found:
        await event.client.edit_message(
            CHANNEL_ID,
            msg_id,
            link_preview=False,
            buttons=[
                Button.inline(f'😊Found', b'Found'),
                Button.url('Click2view', process_link(DOCUMENT_GROUP_ID, document_id))])
    else:
        await event.client.edit_message(
            CHANNEL_ID,
            msg_id,
            link_preview=False,
            buttons=[
                Button.inline(f'😭notFound', b'notFound'),
                Button.url('iHaveThis', f"https://t.me/{BOT_NAME}?start={msg_id}")])

async def it_is_ad(event, user_id: int) -> None:
    await event.client.send_message(
        user_id,
        (f"The [request you submitted](https://t.me/{CHANNEL_NAME}/{event.original_update.msg_id}) "
         f"appears to contain irrelevant information and has been blocked.\n" 
         f"If you have any questions, please provide clarification in the comments section."))
    await event.edit(
        ("Suspected irrelevant information has been blocked. "
         "If you have any questions, please explain in the comments section."))

async def review_request(event, msg_id: int) -> None:
    admin_id = event.original_update.user_id
    await event.client.send_message(
        admin_id,
        f'What would you like to do with this document?\nhttps://t.me/{CHANNEL_NAME}/{msg_id}',
        buttons=[
            Button.inline('Accept it', b'Review_accept'),
            Button.inline('Reject it', b'Review_reject')
        ])
    logger.info(f'[CALLBACK] [REVIEW] [SEND_REQUEST] {admin_id}')

async def review(event, msg_id: int, is_accept: bool) -> None:
    user_id = select('user_id', 'msg_id', msg_id)
    bot_msg_id = select('bot_msg_id', 'msg_id', msg_id)
    if is_accept:
        if not update('b_status', 1, 'bot_msg_id', bot_msg_id):
            await event.answer('DATABASE ERROR!')
            logger.error(f'[CALLBACK] [DATABASE] [LOG_UPDATE_FR_BOT_MSG_ID] ("b_status", 1, {bot_msg_id})')
        document_id = select('document_id', 'msg_id', msg_id)
        try:
            await event.client.edit_message(
                user_id,
                bot_msg_id,
                ('The literature you were looking for has received a response!\n'
                 'The administrator has assisted in approving it for you.'),
                buttons=Button.url('Archieves', process_link(DOCUMENT_GROUP_ID, document_id))
            )
        except UserIsBlockedError:
            await event.client.send_message(
                DOCUMENT_GROUP_ID,
                (f'This [individual](tg://user?id={user_id}) stopped using the chatbot immediately after submitting the request.\n' 
                 f'Should there be any punitive action, such as a ban?'),
                buttons=[Button.inline('B-A-N!', b'banYES'), Button.inline('Mercy', b'banNo')]
            )
        await change_status(event, msg_id, select('document_id', 'msg_id', msg_id))
    else:
        if not update('b_status', 0, 'bot_msg_id', bot_msg_id):
            await event.answer('DATABASE ERROR!')
            logger.error(f'[CALLBACK] [DATABASE] [LOG_UPDATE_FR_BOT_MSG_ID] ("b_status", 0, {bot_msg_id})')
        try:
            await event.client.edit_message(
                user_id,
                bot_msg_id,
                ('The literature you were looking for has received a response! \n'
                 'However, the administrator has determined it to be incorrect and has rejected it on your behalf.'),
                buttons=Button.url('UrPostedInfo', f'https://t.me/{CHANNEL_NAME}/{msg_id}')
            )
        except UserIsBlockedError:
            await event.client.send_message(
                DOCUMENT_GROUP_ID,
                (f'This [individual](tg://user?id={user_id}) stopped using the chatbot immediately after submitting the request.\n' 
                 f'Should there be any punitive action, such as a ban?'),
                buttons=[Button.inline('B-A-N!', b'banYES'), Button.inline('Mercy', b'banNo')]
            )
        await change_status(event, msg_id, 0, False)
    
    await event.edit('Administrator verification complete~')

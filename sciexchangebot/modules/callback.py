""" sciexchangebot module button clicked """
import re
from telethon import events, Button
from telethon.errors.rpcerrorlist import UserIsBlockedError
from sciexchangebot import bot, config, logger
from ..database import is_in_blacklist, select, update, add_blacklist
from ..listener import process_link
from .get_recent_10_unhelped import get_recent_unhelped_url

CHECK_GROUP_ID = config['check_group_id']

@bot.on(events.CallbackQuery)
async def handler(event):
    msg_id = event.original_update.msg_id
    user_id = event.original_update.user_id
    # if user in blacklist
    if is_in_blacklist(user_id):
        await event.answer(
            (f'你因为 {is_in_blacklist(user_id)} 被禁止使用此服务。详情请联系 @Pentacene\n'
             f'You have been banned from this service. Please contact @Pentacene for more details.'))
        return
    # if 😭未找到notFound has been clicked
    if event.data == b'notFound':
        # by check group, AD
        if user_id in CHECK_GROUP_ID:
            await it_is_ad(event, select('user_id', 'msg_id', msg_id))
            logger.info(f'[DELETE] UID:MID:EVENT = {user_id}:{msg_id}:{event.original_update}')
        else:
            await event.answer('你能来帮帮他么?')
    # if 🤔审核中Checking has been clicked
    elif event.data == b'UnderReview':
        # by check group, review by check group
        if user_id in CHECK_GROUP_ID:
            event.answer('管理员审核~')
            await review_request(event, msg_id)
            logger.info(f'[REVIEW] {msg_id} by {user_id}')
    # if 😊已找到Found has been clicked
    elif event.data == b'Found':
        if user_id == 1012414645:
            event.answer(select('user_id', 'msg_id', msg_id))
    # if Yes has been clicked
    elif event.data == b'YES':
        bot_msg_id = msg_id
        msg_id = select('msg_id', 'bot_msg_id', bot_msg_id)
        document_id = select('document_id', 'bot_msg_id', bot_msg_id)
        await event.answer('恭喜你找到了自己想要的文献!')
        await event.edit(
            f'恭喜你找到了自己想要的文献!\nCongratulations!\n\n{get_recent_unhelped_url()}',
            buttons=Button.url(
                '半永久保存地址',
                process_link(int(config['telegram']['documentgroup']), document_id)))
        if not update('b_status', 1, 'bot_msg_id', bot_msg_id):
            await event.answer('数据库出错，无法更新！')
            logger.error(f'[DATABASE] [LOG_UPDATE_FR_BOT_MSG_ID] ("b_status", 1, {bot_msg_id})')
        await change_status(event, msg_id, document_id)
        logger.info(f'[CHECK] [CURRECT] USER_ID:MSG_ID:DOCUMENT_ID = {user_id}:{msg_id}:{document_id}')
    # if No has been clicked
    elif event.data == b'NO':
        bot_msg_id = msg_id
        await event.answer('那我们再等等看吧')
        await event.edit((
            f'您要找的文献已经有人回复啦!可惜不是你想要的.\n'
            f'Unfortunately, someone send the papers which not your request.\n\n'
            f'{get_recent_unhelped_url()}'))
        if not update('document_id', 0, 'bot_msg_id', bot_msg_id):
            await event.answer('数据库出错，无法删除！')
            logger.error(f'[DATABASE] [LOG_UPDATE_FR_BOT_MSG_ID] ("document_id", 0, {bot_msg_id})')
        logger.info(f'[CHECK] [INCURRECT] USER_ID = {user_id}')
        await change_status(event, msg_id, 0, False)
    elif event.data == b'Review_accept':
        msg = await event.get_message()
        text = msg.text
        msg_id = re.search(f"https://t.me/{config['telegram']['workgroupname']}/([0-9]+)", text).group(1)
        msg_id = int(msg_id)
        await review(event, msg_id, is_accept=True)
        logger.info(f'[REVIEW] [ACCEPT] {msg_id} by {user_id}')
    elif event.data == b'Review_reject':
        msg = await event.get_message()
        text = msg.text
        msg_id = re.search(f"https://t.me/{config['telegram']['workgroupname']}/([0-9]+)", text).group(1)
        msg_id = int(msg_id)
        await review(event, msg_id, is_accept=False)
        logger.info(f'[REVIEW] [REJECT] {msg_id} by {user_id}')
    elif event.data == b'banYes':
        if user_id in CHECK_GROUP_ID:
            ban_id = select('user_id', 'msg_id', msg_id)
            await event.client.edit_permissions(int(config['telegram']['workgroup']), ban_id, view_messages=False)
            await event.client.edit_permissions(int(config['telegram']['documentgroup']), ban_id, view_messages=False)
            add_blacklist(ban_id, '发完需求就直接停止使用了机器人')
            logger.info(f'[BAN] [Button] USER_ID = {ban_id}')
            event.answer('烧了它!')
        else:
            event.answer('不是管理员..就别瞎点啊')
    elif event.data == b'banNo':
        event.answer('你还是心太软')

async def change_status(event, msg_id: int, document_id: int, is_found: bool = True) -> None:
    if is_found:
        await event.client.edit_message(
            int(config['telegram']['workgroup']),
            msg_id,
            link_preview=False,
            buttons=[
                Button.inline(f'😊已找到Found', b'Found'),
                Button.url('点我查看Click2View', process_link(int(config['telegram']['documentgroup']), document_id))])
    else:
        await event.client.edit_message(
            int(config['telegram']['workgroup']),
            msg_id,
            link_preview=False,
            buttons=[
                Button.inline(f'😭未找到notFound', b'notFound'),
                Button.url('如果您有请点我iHaveThis', f"https://t.me/{config['telegram']['name']}?start={msg_id}")])

async def it_is_ad(event, user_id: int) -> None:
    await event.client.send_message(
        user_id,
        (f'你发送的 [请求疑似无用信息被屏蔽](https://t.me/{config["telegram"]["workgroupname"]}/{event.original_update.msg_id}) ,'
         f'如有疑问请评论区说明\n'
         f'[Your message](https://t.me/{config["telegram"]["workgroupname"]}/{event.original_update.msg_id}) '
         f'have been removed since we think you send unnecessary request.'))
    await event.edit('疑似无用信息被屏蔽,如有疑问请评论区说明\nUNNECESSARY REQUEST')

async def review_request(event, msg_id: int) -> None:
    admin_id = event.original_update.user_id
    await event.client.send_message(
        admin_id,
        f'您要对这个文件做什么?\nhttps://t.me/{config["telegram"]["workgroupname"]}/{msg_id}',
        buttons=[
            Button.inline('直接接收', b'Review_accept'),
            Button.inline('无情拒稿', b'Review_reject')
        ])
    logger.info(f'[REVIEW] [SEND_REQUEST] {admin_id}')

async def review(event, msg_id: int, is_accept: bool) -> None:
    user_id = select('user_id', 'msg_id', msg_id)
    bot_msg_id = select('bot_msg_id', 'msg_id', msg_id)
    if is_accept:
        if not update('b_status', 1, 'bot_msg_id', bot_msg_id):
            await event.answer('数据库出错，无法更新！')
            logger.error(f'[DATABASE] [LOG_UPDATE_FR_BOT_MSG_ID] ("b_status", 1, {bot_msg_id})')
        document_id = select('document_id', 'msg_id', msg_id)
        try:
            await event.client.edit_message(
                user_id,
                bot_msg_id,
                ('您要找的文献已经有人回复啦! 管理员已经帮助你审核通过啦\n'
                 'The requested papers was checked by admins. This is what you want. Click the button below.'),
                buttons=Button.url('半永久保存地址', process_link(int(config['telegram']['documentgroup']), document_id))
            )
        except UserIsBlockedError:
            await event.client.send_message(
                int(config['telegram']['documentgroup']),
                f'[这个傻逼](tg://user?id={user_id}) 发完需求就直接停止使用了机器人. 是否封禁?',
                buttons=[Button.inline('封了他!封了他!', b'banYES'), Button.inline('算了吧', b'banNo')]
            )
        await change_status(event, msg_id, select('document_id', 'msg_id', msg_id))
    else:
        if not update('b_status', 0, 'bot_msg_id', bot_msg_id):
            await event.answer('数据库出错，无法更新！')
            logger.error(f'[DATABASE] [LOG_UPDATE_FR_BOT_MSG_ID] ("b_status", 0, {bot_msg_id})')
        try:
            await event.client.edit_message(
                user_id,
                bot_msg_id,
                ('您要找的文献已经有人回复啦! 但管理员发现不是正确的,已经帮你拒稿啦\n'
                 'The requested papers was checked by admins. That is not you wanted. Please wait for next notification.'),
                buttons=Button.url('您的发布信息UrPost', f'https://t.me/{config["telegram"]["workgroupname"]}/{msg_id}')
            )
        except UserIsBlockedError:
            await event.client.send_message(
                int(config['telegram']['documentgroup']),
                f'[这个傻逼](tg://user?id={user_id}) 发完需求就直接停止使用了机器人. 是否封禁?',
                buttons=[Button.inline('封了他!封了他!', b'banYES'), Button.inline('算了吧', b'banNo')]
            )
        await change_status(event, msg_id, 0, False)
    
    await event.edit('管理员验证完成~')

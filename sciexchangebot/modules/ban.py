""" sciexchangebot module ban """
from sciexchangebot import config, logger
from ..listener import listener
from ..database import add_blacklist

CHANNEL_ID = int(config['telegram']['channel_id'])
DOCUMENT_GROUP_ID = int(config['telegram']['document_group_id'])

@listener(incoming=True, command="ban")
async def ban(context):
    if len(context.parameter) < 2:
        await context.reply('/ban <id> <reason>')
        await context.delete()
    else:
        if context.sender.id == 1012414645:
            await context.client.edit_permissions(
                CHANNEL_ID,
                int(context.parameter[0]),
                view_messages=False)
            await context.reply('WORKGROUP OK')
            logger.info(f'[BAN] [WORKGROUP] USER_ID = {context.parameter[0]}')
            await context.client.edit_permissions(
                DOCUMENT_GROUP_ID,
                int(context.parameter[0]),
                view_messages=False)
            await context.reply('DOCUMENTGROUP OK')
            logger.info(f'[BAN] [DOCUMENTGROUP] USER_ID = {context.parameter[0]}')
            add_blacklist(int(context.parameter[0]), context.parameter[1])
            await context.reply('DATABASE OK')
            logger.info(f'[BAN] [DB] USER_ID = {context.parameter[0]}')
            await context.delete()
        else:
            await context.delete()

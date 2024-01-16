""" sciexchangebot modules sendmessage """
from asyncio import sleep
from ..listener import listener
from ..database import all_users

@listener(incoming=True, command="send")
async def send_message(context):
    if len(context.parameter) < 2:
        await context.reply('/send <USER_ID> <context>')
        return

    text = ''
    for i in range(1, len(context.parameter)):
        text = text + '\n' + str(context.parameter[i])

    if context.parameter[0] == 'all':
        user_list = all_users()
        for user in user_list:
            await context.client.send_message(
                int(user),
                (f'**Response of developers:**:\n{text}\n\n'
                 f' If you have any questions, please join the discussion [here](https://t.me/+4_KEIC6HLL02YjVh) .'))
            await sleep(1)

    await context.client.send_message(
        int(context.parameter[0]),
        (f'**Response of developers:**:\n{text}\n\n'
         f' If you have any questions, please join the discussion [here](https://t.me/+4_KEIC6HLL02YjVh) .'))
    await context.reply('sent')

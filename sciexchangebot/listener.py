""" sciexchangebot event listener. """
from os.path import exists
import asyncio
import sys
from time import gmtime, strftime
from traceback import format_exc
import yaml
from telethon import events
from telethon.errors import MessageTooLongError
from telethon.events import StopPropagation
from sciexchangebot import bot, config, logger, BOT_NAME

def listener(**args):
    """ Register an event listener. """
    command = args.get('command', None)
    pattern = args.get('pattern', None)
    ignore_edited = args.get('ignore_edited', False)
    
    if command is not None:
        pattern = fr"^\/{command}(?:@{BOT_NAME}|@{BOT_NAME} | |$)([\s\S]*)"
    if pattern is not None and not pattern.startswith('(?i)'):
        args['pattern'] = f"(?i){pattern}"
    else:
        args['pattern'] = pattern
    if 'ignore_edited' in args:
        del args['ignore_edited']
    if 'command' in args:
        del args['command']

    def decorator(function):

        async def handler(context):
            try:
                try:
                    parameter = context.pattern_match.group(1).split(' ')
                    if parameter == ['']:
                        parameter = []
                    context.parameter = parameter
                    context.arguments = context.pattern_match.group(1)
                except BaseException:
                    context.parameter = None
                    context.arguments = None
                await function(context)
            except StopPropagation:
                raise StopPropagation
            except MessageTooLongError:
                await context.edit("Error too long.")
            except BaseException:
                exc_info = sys.exc_info()[1]
                exc_format = format_exc()
                report = f"{BOT_NAME}: \n" \
                            f"# Generated: {strftime('%H:%M %d/%m/%Y', gmtime())}. \n" \
                            f"# ChatID: {str(context.chat_id)}. \n" \
                            f"# UserID: {str(context.sender_id)}. \n" \
                            f"# Message: \n-----BEGIN TARGET MESSAGE-----\n" \
                            f"{context.text}\n-----END TARGET MESSAGE-----\n" \
                            f"# Traceback: \n-----BEGIN TRACEBACK-----\n" \
                            f"{str(exc_format)}\n-----END TRACEBACK-----\n" \
                            f"# Error: \"{str(exc_info)}\". \n"
                await send_log(report, int(config['telegram']['admingroup']))
            
        if not ignore_edited:
            bot.add_event_handler(handler, events.MessageEdited(**args))
        bot.add_event_handler(handler, events.NewMessage(**args))

        return handler
    
    return decorator

async def execute(command: str, pass_error: bool = True):
    """ Executes command and returns output, with the option of enabling stderr. """
    executor = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await executor.communicate()
    if pass_error:
        result = str(stdout.decode().strip()) \
                 + str(stderr.decode().strip())
    else:
        result = str(stdout.decode().strip())
    return result

async def send_log(plaintext: str, chat_id: int) -> None:
    """ Send plaintext as text """
    await bot.send_message(
        chat_id,
        plaintext
    )

async def notification(context, message: str, delete_time: int = 5, delete_original: bool = False) -> None:
    """ Send Notification and delete it after some seconds """
    notification_message = await context.reply(message)
    if delete_original:
        try:
            await context.delete()
        except Exception as e:
            logger.warning(f'notification delele original error: {e}')
    await asyncio.sleep(delete_time)
    await notification_message.delete()
    return

def process_link(chat_id: int, message_id: int) -> str:
    """ return telegram link """
    if chat_id < 0:
        return f'https://t.me/c/{(chat_id + 1000000000000) * (-1)}/{message_id}'
    elif chat_id > 0:
        return f'https://t.me/c/{chat_id}/{message_id}'
    else:
        return ''

def set_state(name: str, state, file_name: str) -> bool:
    try:
        if exists(file_name):
            with open(file_name) as f:
                doc = yaml.safe_load(f)
            doc[name] = state
            with open(file_name, 'w') as f:
                yaml.safe_dump(doc, f, default_flow_style=False)
        else:
            dc = {name: state}
            with open(file_name, 'w', encoding='utf-8') as f:
                yaml.dump(dc, f)
        return True
    except Exception as e:
        logger.warning(f'set_state error: {e}')
        return False

async def get_name(context, at: bool=True) -> str:
    """ return name """
    try:
        sender = context.sender
    except:
        sender = None
        return 'None'
    first_name = sender.first_name
    if sender.last_name is None:
        last_name = ''
    else:
        last_name = sender.last_name
    full_name = f'{first_name} {last_name}'
    uid = sender.id
    if at:
        return f'[{full_name}](tg://user?id={uid})'
    else:
        return full_name


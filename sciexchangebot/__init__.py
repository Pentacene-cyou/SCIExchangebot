""" sciexchangebot initialization """
import logging
import time
from os import getcwd
import yaml
from coloredlogs import ColoredFormatter
from telethon import TelegramClient

BOT_NAME = 'sciexchangebot'

# set up logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.ERROR)
LOGGING_FORMAT = "%(levelname)s [%(asctime)s] [%(name)s] %(message)s"
date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
file_handler = logging.FileHandler(f'./log/{date}.log', 'a', 'utf-8')
file_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
root_logger.addHandler(file_handler)
logging_handler = logging.StreamHandler()
logging_handler.setFormatter(ColoredFormatter(LOGGING_FORMAT))
root_logger.addHandler(logging_handler)
logger = logging.getLogger(f'{BOT_NAME}')
logger.setLevel(logging.DEBUG)

working_dir = getcwd()
help_messages = {}

logger.info(f"{BOT_NAME} load")
config = yaml.load(open(r"config.yml"), Loader=yaml.FullLoader)
bot = TelegramClient(
        f"{BOT_NAME}",
        config['api_key'],
        config['api_hash']).start(bot_token=config['telegram']['TOKEN'])

async def log(message):
    """
    log text message to admingroup
    """
    logger.info(
        message.replace('`', '\"').replace('\n', '    ')
    )
    await bot.send_message(
        int(config['telegram']['admin_group']),
        f'sciexchangebot\nlog message\n{message}')    

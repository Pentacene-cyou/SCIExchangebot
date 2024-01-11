""" sciexchangebot launch sequence. """
from importlib import import_module
from sciexchangebot import bot, logger, BOT_NAME
from sciexchangebot.modules import module_list

bot.start()
for module_name in module_list:
    try:
        import_module(f"{BOT_NAME}.modules." + module_name)
    except BaseException as exception:
        logger.error(f"module {module_name} error: {type(exception)}: {exception}")

logger.info(f"{BOT_NAME} start")
bot.run_until_disconnected()

""" sciexchangebot module init. """
from os.path import dirname, basename, isfile
from glob import glob
from sciexchangebot import logger

def __list_modules():
    module_paths = glob(dirname(__file__) + "/*.py")
    result = [
        basename(file)[:-3]
        for file in module_paths
        if isfile(file) and file.endswith(".py") and not file.endswith("__init__.py")
    ]
    return result
module_list_string = ""
for module in sorted(__list_modules()):
    module_list_string += f"{module}, "
module_list_string = module_list_string[:-2]
module_list = sorted(__list_modules())
logger.info("Loading modules: %s", module_list_string)
__all__ = __list_modules() + ["module_list"]

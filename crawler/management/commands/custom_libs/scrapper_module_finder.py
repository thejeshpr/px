import importlib
import logging
import os
import sys

logger = logging.getLogger(__name__)

def get_scrapper(name):

    # parent_path = os.path.dirname(os.path.realpath(__file__))
    # base_path = os.path.dirname(parent_path)
    # #base_path = "/home/ubuntu/pyenvs/projectx_dev/src/projectx/crawler_backend"
    # files = os.listdir(parent_path)
    # # files = os.listdir("./crawler_backend")
    # # print(parent_path, base_path)
    #
    # module_files = list(filter(lambda x: x.endswith(".py") and x.startswith("cb_"), files))
    #
    folder_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    scrapper_folder_path = os.path.join(folder_path, "scrappers")
    files = os.listdir(scrapper_folder_path)
    module_files = list(filter(lambda x: x.endswith(".py") and x.startswith("cb_"), files))
    logger.debug(f"all module files: {module_files}")

    scrpr_mod_name = f"{name}.py"
    logger.debug(f"scrapper name: {scrpr_mod_name}")

    sys.path.append(scrapper_folder_path)

    if scrpr_mod_name in module_files:
        mod = importlib.import_module(name)
        if hasattr(mod, "scrape"):
            return mod.scrape
    else:
        raise Exception(f"invalid scrapper name: {name}")
        # print ("No Module found")


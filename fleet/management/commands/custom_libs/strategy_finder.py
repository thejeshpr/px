import importlib
import logging
import os
import sys

logger = logging.getLogger(__name__)

def get_strategy(name):
    folder_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    strategy_folder_path = os.path.join(folder_path, "strategies")
    files = os.listdir(strategy_folder_path)
    module_files = list(filter(lambda x: x.endswith(".py") and x.startswith("st_"), files))
    logger.debug(f"all module files: {module_files}")

    strategy_mod_name = f"{name}.py"
    logger.debug(f"strategy name: {strategy_mod_name}")

    sys.path.append(strategy_folder_path)

    if strategy_mod_name in module_files:
        mod = importlib.import_module(name)
        if hasattr(mod, "instructions"):
            return mod.instructions
    else:
        raise Exception(f"invalid strategy name: {name}")



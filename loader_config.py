
import nuke
import os
import logging
# ----------------------------------------------
# INSTRUCTIONS:
# Modify this file as needed. Do not rename it.
# Place it in your python path (i.e. next to loader.py, or in your /.nuke folder).
# ----------------------------------------------

# ----------------------------------------------
# 1. MAIN DEFAULTS
# ----------------------------------------------

EXECUTION_SHORTCUT = "Shift+E"

# Root folder where your projects are stored. Usually it is assigned to an environment variable(i.e. "MY_PRJ_ROOT"). This variable should be set to that variable. It is required to have this set to environment variable.
# You can  set a project root vaaiable using code below.
# os.environ["MY_PRJ_ROOT"] = "/path/to/root"
ROOT_PATH = "MY_PRJ_ROOT"

# Project name is the folder name of your project that is in project root. In pipelines usually it is assigned to a variable. If not you can ignore this variable and use a string query instead.
PRJ_NAME = "MY_PROJECT_ABBR"

# The version prefix is usually starting with "v"(i.e. v001, v01) but in case you use different prefix, change it here.
VERSION_PREFIX = "v"

# ----------------------------------------------
# 2. LOAD SETTINGS
# ----------------------------------------------
# If set to True connects loaded node to the loader node's output. Connect loaded node to the loader if set to False.
reconnect = False

# Position(x, y) of the loaded node relative to the loader
position = "0 -100"

# Delete loader node after execution.
delete_after = False

# Select loaded node
select_loaded = True

# If query return multiple files, choose which one to load. Available options "all", "first" and "last"
load = "all"

# Use deep read to read in the file
deep = False

# Use camera node to load 3d file(.abc)
camera = False

# Use classic 3d nodes(old 3d system) to load the 3d file.
classic3d = True

# ----------------------------------------------
# 3. DEFAULT QUERY
# ----------------------------------------------
# This is the search query that will be loaded by default when you create a loader node.
# Every item in the dict. below is a search line.
default_query = {
    "root": "${}$".format(ROOT_PATH),
    "show": "${}$".format(PRJ_NAME),
    "seq": "$MY_SEQUENCE$",
    "shot": "$MY_SHOT$",
    "task": "comp",
    "version": "v:latest",
    "filename": r"re:\w+[\._]\d+\.exr$",
    }


# ----------------------------------------------
# 4. DEFAULT SETTINGS
# ----------------------------------------------
# This is the settings that will be displayed when you create a loader node.
# It can be the settings that is visibe to the user, and may not contain all the settings variable listeg in section 2.
default_settings = {
    "position": position,
    "select_loaded": str(select_loaded),
    "load": load,
    "camera": "False",
    }


# ----------------------------------------------
# 5. FORMATS
# ----------------------------------------------
# Different formats that loader can load. It can load Images(read node), geometry(geo node), script.
# Add new formats in lists below to add support for more formats (i.e. .tif).

formats = {
    "image": [".exr", ".png", ".jpg", ".dpx"],
    "geo": [".abc", ".usd", ".obj", ".fbx"],
    "script": [".nk", ".gizmo"]
}


# ----------------------------------------------
# DO NOT CHANGE.
# ----------------------------------------------
# Setup logging
def get_logger(name="loader", log_file=None, level=logging.INFO):
    """Create and configure a logger specifically for the plugin."""
    # Create a custom logger
    logger = logging.getLogger(name)

    # Prevent propagation to the root logger
    logger.propagate = False

    # Set the logging level
    logger.setLevel(level)

    # Create handlers
    console_handler = logging.StreamHandler()  # Log to console
    handlers = [console_handler]

    if log_file:
        file_handler = logging.FileHandler(log_file)  # Log to file
        handlers.append(file_handler)

    # Create a formatter and set it for the handlers
    formatter = logging.Formatter(
        "%(name)s - %(levelname)s - %(message)s"
    )
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# Please ignore the dict. below.
defaults = {
    "reconnect": str(reconnect),
    "position": position,
    "delete_after": str(delete_after),
    "select_loaded": str(select_loaded),
    "load": load,
    "deep": str(deep),
    "classic3d": str(classic3d),
    "camera": str(camera),
    }

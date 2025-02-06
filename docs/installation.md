# 🛠️ Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/harut-harutyunyan/loader.git
   ```
2. Copy the loader folder and paste it anywhere in your plugin path (like in ~/.nuke).
3. Open the file init.py inside your ~/.nuke folder with a text editor, or create it if it
doesn’t exist.
4. Add the following lines:
   ```python
   import nuke
   nuke.pluginAddPath("./loader")
   ```

# 🛠️ Configuration

**The configuration is optional. You can completely ignore this section, however it will be much easier to use the Loader when having it configured for you.**

Inside the loader folder you can find `loader_config.py` configuration file. This file will let you configure the Loader and get the most out of it.
The configuration is very simple. There are some default values that you need to set inside `loader_config.py` file.

### Execution Shortcut
Defines the keyboard shortcut to execute the plugin:
```python
EXECUTION_SHORTCUT = "Shift+E"
```

### Root Path
Usually in pipelines all the projects are stored in some directory. And path to this directory is set as an *environment variable*. `ROOT_PATH` should be set to that variable's name. So the loader will resolve it to the path at execution time.
```python
ROOT_PATH = "MY_PRJ_ROOT"
```

### Project Name
The folder name of the project, usually assigned as a variable:
```python
PRJ_NAME = "MY_PROJECT_ABBR"
```

### Version Prefix
Prefix for versioning (e.g., `v001`, `v01`):
```python
VERSION_PREFIX = "v"
```

***
[< Previous](./README.md) | [Next>](./query.md)

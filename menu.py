import loader_config
import loader_node
from loader_widget import QueryWidget, ExecutionBtns


m = nuke.menu('Nuke')
m.addCommand('Edit/Loader/Create Loader', 'import loader_node\nloader_node.LoaderNode.create_node()')
m.addCommand('Edit/Loader/Load Selected', 'import loader_node\nloader_node.load_selected()', loader_config.EXECUTION_SHORTCUT)

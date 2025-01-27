import os
import re
import json
import logging
import nuke

import loader_config
from loader import PathsHandler


DOCS_URL = "https://github.com/harut-harutyunyan/loader/blob/master/README.md"

loader_logger = loader_config.get_logger()

knob_changed = """
n = nuke.thisNode()
k = nuke.thisKnob()
if k.name() == "show_analize":
    n["file"].setVisible(k.getValue()==1)
    n["analize"].setVisible(k.getValue()==1)
if k.name() == "inputChange":
    inpt = n.input(0)
    if inpt:
        n["show_analize"].setValue(1)
        n["file"].setVisible(True)
        n["analize"].setVisible(True)
        knob = inpt.knob("file")
        if knob:
            n["file"].setValue(knob.getValue())
            n["file"].setEnabled(False)
    else:
        n["file"].setEnabled(True)

if k.name() == "query_storage":
    try:
        n.knob('query').getObject().populate()
    except:
        pass
if k.name() == "settings_storage":
    try:
        n.knob('load_settings').getObject().populate()
    except:
        pass
"""

class LoaderNode(object):

    @classmethod
    def __empty_group(cls):
        node = nuke.createNode("Group")
        node.begin()
        input = nuke.nodes.Input()
        input.setName("Input")
        output = nuke.nodes.Output()
        output.setInput(0, input)
        node.end()
        return node

    @classmethod
    def create_node(cls):
        node = nuke.createNode("NoOp")
        node['knobChanged'].setValue(knob_changed)
        node['tile_color'].setValue(2234897919)
        node.setName("Loader1")
        
        knob = nuke.Tab_Knob("loader", "Loader")
        node.addKnob(knob)
        
        # docs 
        knob = nuke.PyScript_Knob("docs", "Documentation", "import webbrowser\nwebbrowser.open(\"{}\")".format(DOCS_URL))
        node.addKnob(knob)
        knob = nuke.Text_Knob("div1", "")
        node.addKnob(knob)
        
        # analize        
        knob = nuke.Boolean_Knob("show_analize", "analize path")
        node.addKnob(knob)
        
        knob = nuke.File_Knob('file', '')
        knob.setVisible(False)
        knob.clearFlag(nuke.STARTLINE)
        node.addKnob(knob)
        
        knob = nuke.PyScript_Knob("analize", "Analize", "from loader_node import LoaderNode\nLoaderNode.analize()")
        knob.setVisible(False)
        knob.clearFlag(nuke.STARTLINE)
        node.addKnob(knob)
        
        knob = nuke.Text_Knob("div2", "")
        node.addKnob(knob)
        
        # create storage knobs
        knob = nuke.String_Knob('query_storage')
        knob.setEnabled(False)
        knob.setVisible(False)
        knob.setValue("[]")
        node.addKnob(knob)
        
        knob = nuke.String_Knob('settings_storage')
        knob.setEnabled(False)
        knob.setVisible(False)
        knob.setValue("[]")
        node.addKnob(knob)
        
        # query widgets
        knob = nuke.PyCustom_Knob("query", "", "QueryWidget(nuke.thisNode(), 'query_storage') if 'QueryWidget' in globals() else type('Dummy', (), {'makeUI': classmethod(lambda self: None)})")
        knob.setFlag(nuke.STARTLINE)
        node.addKnob(knob)
        knob = nuke.Text_Knob("div2", "")
        node.addKnob(knob)
        knob = nuke.PyCustom_Knob("load_settings", "", "QueryWidget(nuke.thisNode(), 'settings_storage') if 'QueryWidget' in globals() else type('Dummy', (), {'makeUI': classmethod(lambda self: None)})")
        knob.setFlag(nuke.STARTLINE)
        node.addKnob(knob)
        
        node['query_storage'].setValue(json.dumps([list(i) for i in loader_config.default_query.items()]))
        node['settings_storage'].setValue(json.dumps([list(i) for i in loader_config.default_settings.items()]))
        
        #execution
        knob = nuke.PyScript_Knob("_execute", "execute", "from loader_node import LoaderNode\nLoaderNode.execute(nuke.thisNode())")
        knob.setVisible(False)
        node.addKnob(knob)
        knob = nuke.PyScript_Knob("_validate", "validate", "from loader_node import LoaderNode\nLoaderNode.validate(nuke.thisNode())")
        knob.setVisible(False)
        node.addKnob(knob)
        knob = nuke.PyCustom_Knob("execution_qt", "", "ExecutionBtns(nuke.thisNode()) if 'ExecutionBtns' in globals() else type('Dummy', (), {'makeUI': classmethod(lambda self: None)})")
        knob.setFlag(nuke.STARTLINE)
        node.addKnob(knob)
        
        #credit
        knob = nuke.Text_Knob("div3", "")
        node.addKnob(knob)
        knob = nuke.Text_Knob("credit", "",
                              "<font><br/><b><a href=\"https://linktr.ee/har8unyan\" style=\"color:#666\">Harut Harutyunyan</a></b></font>",
                              )
        knob.setTooltip("© Harut Harutyunyan\nhar8unyan@gmail.com\n2024")
        knob.setFlag(nuke.STARTLINE)
        node.addKnob(knob)
        
        # python tab
        knob = nuke.Tab_Knob("python", "Python")
        node.addKnob(knob)
        
        # knob = nuke.Multiline_Eval_String_Knob('on_pre_load', 'Before Loading')
        # node.addKnob(knob)
        
        knob = nuke.Multiline_Eval_String_Knob('on_post_load', 'After Loading')
        node.addKnob(knob)

    @staticmethod
    def parse_position_input(input_string):
        if re.match(r"^-?\d+\s-?\d+$", input_string):
            numbers = input_string.split()
            int_numbers = [int(num) for num in numbers]
            return int_numbers
        else:
            return [int(num) for num in loader_config.position.split()]

    @staticmethod
    def deselect_all():
        [n.setSelected(False) for n in nuke.selectedNodes()]

    @classmethod
    def get_query_list(cls, node):
        storage_value = json.loads(node["query_storage"].getText())

        query_list = []
        for n in storage_value:
            value = n[1]
            if "[parent." in value:
                index = value.index("[")
                parent_string = value[index:]
                _, node, knob = parent_string[1:-1].split(".")
                node = nuke.toNode(node)
                if node and node.knob(knob):
                    parent_value = str(node[knob].value())
                else:
                    parent_value = ""
                value = value.replace(parent_string, parent_value)
            query_list.append(value)
        
        return query_list

    @classmethod
    def get_load_settings(cls, node):
        storage_value = json.loads(node["settings_storage"].getText())
        storage_value = {item[0]: item[1] for item in storage_value}
        load_settings = {**loader_config.defaults, **storage_value}
        
        return load_settings
        
    @classmethod
    def __load(cls, query_list):
        return PathsHandler.construct_file_paths(query_list)
        
    @classmethod
    def validate(cls, node):
        query_list = cls.get_query_list(node)

        file_list = PathsHandler.construct_file_paths(query_list)
        if file_list:
            for i in file_list:
                loader_logger.info(PathsHandler.sequence_path(i))
                return True
        else:
            loader_logger.info("Failed to construct file path with given parameters")
            loader_logger.info(query_list)
            return False

    @classmethod
    def how_many_to_load(cls, count, sequences):
        if count == "first":
            return [sequences[0]]
        elif count == "last":
            return [sequences[-1]]
        elif count.isdigit():
            return sequences[:int(count)]
        
        return sequences

    @classmethod
    def create_image_node(cls, seq_path, deep):
        if deep == "True":
            read = nuke.nodes.DeepRead()
        else:
            read = nuke.nodes.Read()
        read.knob("file").fromUserText(seq_path)
        
        return read

    @classmethod
    def create_geo_node(cls, seq_path, load_settings):
        if load_settings["classic3d"] == "False":
            read_geo = nuke.nodes.GeoImport
            camera = nuke.nodes.Camera4
        else:
            read_geo = nuke.nodes.ReadGeo2
            camera = nuke.nodes.Camera3
        
        if load_settings["camera"] == "True":
            node = camera()
            if load_settings["classic3d"] == "False":
                node.knob("import_enabled").setValue(1)
            else:
                node.knob("read_from_file").setValue(1)
        else:
            node = read_geo()
            
        node.knob("file").setValue(seq_path)
        return node

    @classmethod
    def load_nuke_script(cls, script_path):
        nuke.nodePaste(script_path)
        script_content = nuke.selectedNodes()
        if len(script_content) == 1:
            return script_content[0]
        else:
            return None

    @classmethod
    def spawn_node(cls, seq, load_settings):
        seq_path = PathsHandler.sequence_path(seq)
        ext = os.path.splitext(str(seq))[-1]
        if ext in loader_config.formats["image"]:
            node = cls.create_image_node(seq_path, load_settings["deep"])
        elif ext in loader_config.formats["geo"]:
            node = cls.create_geo_node(seq_path, load_settings)
        elif ext in loader_config.formats["script"]:
            node = cls.load_nuke_script(seq_path)
        else:
            print("unknown formt {}. Skipping {}...".format(ext, str(seq)))
            return
        
        node.setSelected(load_settings["select_loaded"]=="True")
        
        return node

    @classmethod
    def run_post_load_script(cls, loader, loaded):
        script = loader["on_post_load"].getText()
        if script != "" and loaded:
            post_script = "loader = nuke.toNode(\"{}\")\n".format(loader.name())
            post_script += "loaded = [nuke.toNode(n) for n in \"{}\".split(\",\")]\n".format(",".join([n.name() for n in loaded]))
            post_script += script
            exec(post_script)
              
    @classmethod
    def connect_node(cls, loader, loaded, reconnect):
        if reconnect:
            for dep in loader.dependent():
                for i in range(dep.inputs()):
                    if dep.input(i) is loader:
                        dep.setInput(i, loaded)
        else:
            loader.setInput(0, loaded)
                  
    @classmethod
    def execute(cls, node):
        load_settings = cls.get_load_settings(node)

        query_list = cls.get_query_list(node)
        sequences = cls.__load(query_list)
        
        sequences = cls.how_many_to_load(load_settings["load"], sequences)
        
        # get position
        posx, posy = cls.parse_position_input(load_settings["position"])
        posx += node.xpos()
        posy += node.ypos()
        
        cls.deselect_all()
        
        loaded = []
        for seq in sequences:
            read = cls.spawn_node(seq, load_settings)
            if read:
                loaded.append(read)
            
                # set position 
                read.setXYpos(posx, posy)
                posx += 100
        
        if len(loaded)>0:
            cls.connect_node(node, loaded[0], load_settings["reconnect"]=="True")
         
        cls.run_post_load_script(node, loaded)
        
        if load_settings["delete_after"] == "True":
            nuke.delete(node)
    
    @staticmethod
    def check_sequence(filename):
        pattern = r'^\w+([\._]\d+)\.\w+$'
        return bool(re.match(pattern, filename))
        
    @classmethod
    def analize(cls):
        node = nuke.thisNode()
        knob = node.knob("file")
        filepath = knob.getEvaluatedValue()
        if os.path.exists(os.path.dirname(filepath)):
            _, filename = os.path.split(filepath)
            prj_root = os.getenv(loader_config.project_root, "")
            prj_name = os.getenv(loader_config.project_name, "")
            project_dir = "{}/{}/".format(prj_root, prj_name)
            filepath = os.path.dirname(filepath.replace(project_dir, ""))
            
            query_storage = [list(i) for i in loader_config.default_query.items()]
            query_storage.extend([["search", i] for i in filepath.split("/")])

            if cls.check_sequence(filename):
                filename_query = r"re:\w+[\._]\d+\{}$".format(os.path.splitext(filename)[1])
            else:
                filename_query = r're:\w+\{}$'.format(os.path.splitext(filename)[1])
                
            query_storage.append(["filename", filename_query])
            node["query_storage"].setValue(json.dumps(query_storage))
            

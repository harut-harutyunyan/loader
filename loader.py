import os
import re
import json
from pathlib import Path

import loader_config
import third_party.pyseq as pyseq

class PathsHandler(object):

    PRJ_ROOT = os.getenv(loader_config.project_root, "")
    PRJ_NAME = os.getenv(loader_config.project_name, "")

    VERSION_PREFIX = loader_config.version_prefix

    @staticmethod
    def sequence_path(seq: pyseq.Sequence) -> str:
        """Return full path of a pyseq sequence(directory + filename)
        /prj/train/abc010/abc010_0025/plate/abc010_0025_fg01.1001.exr"""
        
        if seq.length() > 1:
            padding = "%{}d".format(format(len(seq[0].replace(seq.head(), "").replace(seq.tail(), "")), '02'))
            seq_path = "{}{}{}".format(seq.format('%D%h'), padding, seq.format("%t %r"))
        else:
            seq_path = seq.path()
            
        return seq_path

    @classmethod
    def _version_get(cls, string: str) -> str:
        """Extract version information from filenames used by DD (and Weta, apparently)
        These are _v# or /v# or .v# where v is a prefix string, in our case
        we use "v" for render version and "c" for camera track version.
        See the version.py and camera.py plugins for usage."""

        if string is None:
            raise ValueError("Empty version string - no match")
        if string.startswith(PathsHandler.VERSION_PREFIX):
            string = "_"+string
        regex = "[/_.]"+PathsHandler.VERSION_PREFIX+"\d+"
        matches = re.findall(regex, string, re.IGNORECASE)
        if not len(matches):
            return ""
        return re.search("\d+", matches[-1:][0]).group()
    
    @classmethod
    def _get_all_versions(cls, file_list: list) -> list:
        """Loop over file_list and return the files that contain version information
        return format is a list containing a list of Path object and version number.
        [[Path(/prj/foo_v001.exr), "001"]]"""
        
        all_versions = []
        for obj in file_list:
            version = PathsHandler._version_get(obj.name)
            if version:
                all_versions.append((obj, version))
        
        return all_versions
    
    @classmethod
    def _handle_env(cls, string: str) -> str:
        """Check if string contains env variable encapsulated in $ for example $MY_VAR$
        and replace it with environment variable value if it exists."""
        
        pattern = r'\$[^\$]+\$'
        matches = re.findall(pattern, string)

        if matches:
            matches = list(set(matches))
            for m in matches:
                var = os.getenv(m[1:-1], "")
                if var:
                    string = string.replace(m, var)
                
        return string
        
    @classmethod
    def _handle_string(cls, parent_dir: Path, string: str) -> list:
        """If the strig path exists in parent dir will return the list of Path objects of the filename"""
        string = cls._handle_env(string)
        end_path = parent_dir.joinpath(string)
        if end_path.exists():
            return [end_path]
        return []
    
    @classmethod
    def _handle_python(cls, parent_dir: Path, string: str) -> list:
        code = "pd=\"{}\"\n".format(str(parent_dir))
        code += string[3:]
        namespace = {}
        exec(code, namespace)
        
        res = namespace.get("res", None)
        if not isinstance(res, list):
            return []
        if isinstance(res, str):
            res=[res]
        
        reuslts = []
        for i in res:
            py_path = parent_dir.joinpath(str(i))
            if py_path.exists():
                reuslts.append(py_path)
        
        return reuslts
        
    @classmethod
    def _handle_regex(cls, parent_dir: Path, string: str) -> list:
        pattern = string[3:]
        pattern = cls._handle_env(pattern)
        match_list = []
        
        if parent_dir.is_dir():
            for item in parent_dir.iterdir():
                if re.match(pattern, item.name):
                    match_list.append(item)
                    
        return match_list

    @classmethod
    def _handle_version(cls, parent_dir: Path, string: str, file_list=None) -> list:
        ver = string[2:]
        
        if not parent_dir.is_dir():
            return []

        if file_list == None:
            file_list =  list(parent_dir.iterdir())
        all_versions = cls._get_all_versions(file_list)
        if ver.isdigit():
            return [i[0] for i in all_versions if int(i[1]) == int(ver)]
        elif ver=="all":
            return [i[0] for i in all_versions]
        elif ver=="latest":
            latest = [int(i[1]) for i in all_versions]
            if latest:
                return cls._handle_version(parent_dir, "v:{}".format(max(latest)), file_list)
            return []
        elif ver.startswith("-") and ver[1:].isdigit():
            versions = sorted([int(i[1]) for i in all_versions], reverse=True)
            if versions:
                return cls._handle_version(parent_dir, "v:{}".format(versions[int(ver[1:])%len(versions)]), file_list)
            return []
        else:
            return []
        
    @classmethod
    def _handle_nested(cls, parent_dir: Path, string: str) -> list:
        string = string[1:]
        match_list = []
        for item in parent_dir.glob("**/*"):
            match_list.extend([i for i in cls._search_path(item.parent, string)])
        
        return list(set(match_list))
    
    @classmethod
    def _search_path(cls, parent_dir: Path, string: str) -> list:
        
        string = string.strip()
        version_string = None
        if "&&" in string:
            string, version_string = string.split("&&")
            string = string.strip()
            version_string = version_string.strip()
            
        if string.startswith("*"):
            results = cls._handle_nested(parent_dir, string)
        elif string.startswith("py:"):
            results = cls._handle_python(parent_dir, string)
        elif string.startswith("re:"):
            results = cls._handle_regex(parent_dir, string)
        elif string.startswith("v:"):
            results = cls._handle_version(parent_dir, string)
        else:
            results = cls._handle_string(parent_dir, string)

        if version_string and version_string.startswith("v:"):
            return cls._handle_version(parent_dir, version_string, results)
        return results
    
    @classmethod
    def _construct_file_paths(cls, string_list: list, current_path=Path()) -> list:
        if not string_list:
            return [current_path]

        string, *tail = string_list
        results = []

        for path in cls._search_path(current_path, string):
            results.extend(cls._construct_file_paths(tail, path))

        return results
    
    @classmethod
    def __old_construct_file_paths(cls, string_list: list) -> list:

        results = []
        file_paths = [f for f in PathsHandler._construct_file_paths(string_list) if f.is_file()]
        parent_paths = list({path.parent for path in file_paths})
        for path in parent_paths:
            seqs = pyseq.get_sequences(str(path))
            results.extend(seqs)

        return results

    @classmethod
    def construct_file_paths(cls, string_list: list) -> list:

        results = []
        files = [f for f in PathsHandler._construct_file_paths(string_list) if f.is_file()]
        directory_groups = {}
        for file_path in files:
            directory_path = file_path.parent
            if directory_path not in directory_groups:
                directory_groups[directory_path] = []
            directory_groups[directory_path].append(str(file_path))
        for i in list(directory_groups.values()):
            seqs = pyseq.get_sequences(i)
            results.extend(seqs)
        
        return results

if __name__ == '__main__':
    # multiple files
    multi_string = Path("/Users/harut/Documents/harut/prj/train/multy")
    #
    sample_string = "/Users/harut/Documents/harut/prj/train/abc010/abc010_0020/plate/fg01/v001/exr/int010_0020.%04d.exr"
    #
    sample_list = [
                    "$MY_PRJ_ROOT$",
                    "$MY_PROJECT_ABBR$",
                    "abc010",
                    "abc010_0025",
                    "comp",
                    # "fg01",
                    # "v:latest",
                    # "exr",
                    r"re:\w+\.nk$ && v:latest",
                    ]

    root = Path("/Users/harut/Documents/harut/prj/train/abc010/abc010_0020/plate")

    for i in PathsHandler.construct_file_paths(sample_list):
        print(PathsHandler.sequence_path(i))

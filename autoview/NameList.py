from autoview.FileExtFinder import FileExtFinder, FileNameFinder
from typing import Dict, List

class NameValues(object):
    """
    Represent a list of values that belong to one specific name.

    Attributes
    ----------
    None

    Methods
    -------
    `setName(name: str)`
        Set the name of the values.
    
    `setVlist(vlist: List)`
        Set the values in a list.

    `appendVlist(*vs)`
        Append some values into the existing value list.
    """
    def __init__(self):
        self.name = ""
        self.vlist = []

    def setName(self, name: str):
        self.name = name 
        return self

    def setVlist(self, vlist: List): 
        self.vlist.extend(vlist)
        return self

    def appendVlist(self, *vs):
        self.vlist.extend(vs)
        return self

class NameList(object):
    """
    Represent the list of `NameValues`.

    Attributes
    ----------
    `name_list`
        A `List` of `NameValues`.

    Methods
    -------
    `buildNameList`
        Virtual function that needs to be implemented by son classes.

    `combineNameList(that)`
        Combine another `NameList` instance into `this` one.

    `__str__`
        Automatically serialized as string.

    `__getitem__(name)`
        Access a list of values by name.

    """
    def __init__(self):
        self.name_list = []

    def buildNameList(self): ...

    def combineNameList(self, that):
        ret = NameList()
        for this_nv in self.name_list:
            this_name = this_nv.name 
            for that_nv in that.name_list:
                that_name = that_nv.name 
                nv = NameValues()
                nv.name = this_name + '_' + that_name
                nv.vlist.append(this_name)
                nv.vlist.append(that_name)
                ret.name_list.append(nv)
        return ret

    def __str__(self):
        s = "{\n"
        for nv in self.name_list:
            s += "\t{name}:{vlist}\n".format(name=nv.name, vlist=nv.vlist)
        s += "}"
        return s

    def __getitem__(self, name: str):
        ret = []
        for nv in self.name_list:
            if name == nv.name:
                ret = nv.vlist
            else: 
                print("no name {name}".format(name=name))
        return ret

class QrcList(NameList):
    # all the qrcTechFile should end with ext: "*.qrc"
    def __init__(self, ext = "qrc"):
        NameList.__init__(self)
        self.qrc_finder = FileExtFinder(ext)

    def buildNameList(self):
        qrc_files = self.qrc_finder()
        for qrc in qrc_files:
            qrc_name = qrc.split(".")[0]
            self.name_list.append(
                NameValues().setName(qrc_name).appendVlist(qrc)
            )

class SdcList(NameList):
    def __init__(self, ext = "sdc"):
        NameList.__init__(self)
        self.sdc_finder = FileExtFinder(ext)

    def buildNameList(self):
        sdc_files = self.sdc_finder()
        for sdc in sdc_files:
            sdc_name = sdc.split(".")[0]
            self.name_list.append(
                NameValues().setName(sdc_name).appendVlist(sdc)
            )

import re 

class LibParser(NameList):
    def __init__(self):
        NameList.__init__(self)

    def pvtExtract(self, path: str):
        op_cond_re = r'operating_conditions\s*\("?(\w+)"?\)\s*{([\s\S]*?)}'
        op_cond_re = re.compile(op_cond_re)
        process_re = re.compile(r'process\s*:\s*([1-9]\d*\.?\d*|0\.\d*[1-9]\d*)')
        voltage_re = re.compile(r'voltage\s*:\s*([1-9]\d*\.?\d*|0\.\d*[1-9]\d*)')
        temp_re    = re.compile(r'temperature\s*:\s*(-?\d+)')
        with open(path) as lib: 
            lib_content = lib.read() 
            opconds = op_cond_re.findall(lib_content)
            for opcond in opconds: 
                opcond_name = opcond[0]
                opcond_pvt = opcond[1]
                p = process_re.findall(opcond_pvt)
                v = voltage_re.findall(opcond_pvt)
                t = temp_re.findall(opcond_pvt)
                self.name_list.append(
                    NameValues().setName(opcond_name).appendVlist(p, v, t)
                )


class LibList(NameList):
    def __init__(self, ext = "lib"):
        NameList.__init__(self)
        self.lib_finder = FileExtFinder(ext)
        self.group_crit = 0

    def setGroupCrit(self, group):
        if group in [0,1,2,4]:
            self.group_crit = group


    def getOpConds(self):
        lib_files = self.lib_finder()
        opconds = NameList()
        for lib in lib_files:
            lib_parser = LibParser()
            lib_parser.pvtExtract(lib)
            opconds.name_list.extend(lib_parser.name_list)
        return opconds

    def buildNameList(self):
        import os
        lib_files = self.lib_finder()
        pvt_names = []
        for lib in lib_files:
            # lib_parser = LibParser()
            # lib_parser.pvtExtract(lib)
            #TODO: group the lib set by crit
            lib_set_name = os.path.split(lib)[0].split("/")[-1]
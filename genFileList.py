from autoview.NameList import *


if __name__ == "__main__":
    nv = NameValues().setName("ss").setVlist(["s", "a", "d"])
    nl = NameList()
    nl.name_list.append(nv)
    print("print name list")
    print(str(nl))
    p = LibParser()
    p.pvtExtract("test.lib")
    print("extract PVT corner:")
    print(str(p))

    ll = LibList()
    print("print all op conds:")
    print(ll.getOpConds())
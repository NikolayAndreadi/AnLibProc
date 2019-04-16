# ALPOrcaIO - module for processing ORCA .inp and .out files

import re
from ALPconstant import *


# MakeInputFile - make .inp file. Requires TheoryLvl, Element, Charge, Multiplicity and XYZ
def MakeInputFile(fn, tl, el, cg, mp, xyz):
    fn = SCRATCHDIR + '/' + tl + '/' + fn + ".inp"
    f = open(fn, 'w+')

    smp = open("./DATA/" + tl, 'r')
    tmpstr = smp.read()
    smp.close()

    tmpstr = tmpstr.replace("#HE", el)
    tmpstr += "\n\n* xyz " + str(cg) + ' ' + str(mp) + '\n' + xyz + "\n*"
    f.write(tmpstr)
    f.close()


# GetMpFromOrcaInp - get multiplicity from Orca input file. Requires filename with path
def GetMpFromOrcaInp(content):
    target = content.find("xyz")
    endtar = content[target:].find('\n') + target

    return content[target:endtar].split()[2]


# GetHeavyAtom - find heavy element in xyz
def GetHeavyAtom(string):
    return [x for x in HEAVYLIST if re.search(x, string)][0]


# GetXyzFromOrcaOut - get xyz from Orca out file. Requires filename with path
def GetOrcaOutXyz(fn):
    f = open(fn, 'r')
    content = f.read()
    f.close()

    target = content.rfind("CARTESIAN COORDINATES (ANGSTROEM)")
    target += 68
    endtar = content[target:].find("----------------------------")
    endtar += target - 2
    return content[target:endtar]


# GetOrcaOutStatus - get status of .out file. Check STATUS dict for info
def GetOrcaOutStatus(content):
    for key, val in STATUS.items():
        if val in content:
            return key
    return 0

#get final energy from orca
def GetOrcaOutE(content):
    target = content.find("FINAL SINGLE POINT ENERGY")
    endtar = content[target:].find('\n') + target

    return content[target:endtar].split()[2]


# End of module ALPOrcaIO

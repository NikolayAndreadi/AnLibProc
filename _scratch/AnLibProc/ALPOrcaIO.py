# ALPOrcaIO - module for processing ORCA .inp and .out files

import re

from ALPconstant import *


def MakeInputFile(fn, tl, el, cg, mp, xyz, retry=False):
    """
    Generating .inp file

    :param fn: filename
    :param tl: theory level
    :param el: heavy atom
    :param cg: charge
    :param mp: multiplicity
    :param xyz: geometry
    :param retry: if true - delete guess HCore line
    :return: None
    """
    fn = SCRATCHDIR + '/' + tl + '/' + fn + ".inp"
    f = open(fn, 'w+')

    smp = open("./DATA/" + tl, 'r')
    tmpstr = smp.read()
    smp.close()

    tmpstr = tmpstr.replace("#HE", el)
    if retry:
        tmpstr = tmpstr.replace("Guess HCore", "")
    tmpstr += "\n\n* xyz " + str(cg) + ' ' + str(mp) + '\n' + xyz + "\n*"
    f.write(tmpstr)
    f.close()


def GetMpFromOrcaInp(content, MultOrCharge):
    """
    Extract multiplicity from Orca files.

    :param content:  opened and read file (.inp or .out)
    :param MultOrCharge: 2 if Multiplicity, 1 if Charge
    :return: multiplicity (int)
    """
    target = content.find("xyz")
    endtar = content[target:].find('\n') + target

    return content[target:endtar].split()[MultOrCharge]


def GetHeavyAtom(string):
    """
    Finds heavy atom in xyz set

    :param string: xyz data set
    :return: heavy atom symbol
    """
    return [x for x in HEAVYLIST if re.search(x, string)][0]


def GetOrcaOutXyz(fn):
    """
    Get xyz from Orca out file.

    :param fn: filename
    :return: xyz data set
    """
    f = open(fn, 'r')
    content = f.read()
    f.close()

    target = content.rfind("CARTESIAN COORDINATES (ANGSTROEM)")
    target += 68
    endtar = content[target:].find("----------------------------")
    endtar += target - 2
    return content[target:endtar]


def GetOrcaOutStatus(content):
    """
    Get status of .out file.

    :param content: opened and read .out file
    :return: status or 0 if unknown error occures
    """
    for key, val in STATUS.items():
        if val in content:
            return key
    return 0


def GetOrcaOutE(content):
    """
    Get final energy from orca out

    :param content: opened and read .out file
    :return: final energy
    """
    target = content.find("FINAL SINGLE POINT ENERGY")
    endtar = content[target:].find('\n') + target

    return content[target:endtar].split()

# End of module ALPOrcaIO

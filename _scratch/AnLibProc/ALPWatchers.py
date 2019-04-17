from collections import Counter
from ALPCSV import *
from ALPDelivery import *
from ALPOrcaIO import *


def WatchLomonosovScript():
    """
    If some files requires computation and script doesn't work - start it

    :return: None
    """
    if not IsInLomonosovSqueue(PBE0):
        N = 0
        for file in os.listdir(SCRATCHDIR + "PBE0/"):
            if file.endswith(".inp"):
                N += 1
        if N >= PBE0MININP:
            run = "sbatch -N3 " + SCRATCHDIR + "PBE0.sh " + "-i " + PBE0 + "/"
            os.system(run)

    if not IsInLomonosovSqueue(MP2):
        N = 0
        for file in os.listdir(SCRATCHDIR + "MP2/"):
            if file.endswith(".inp"):
                N += 1
        if N >= MP2MININP:
            run = "sbatch -N6 -c2 " + SCRATCHDIR + "MP2.sh " + "-i " + MP2 + "/"
            os.system(run)

    if not IsInLomonosovSqueue(MULT):
        N = 0
        for file in os.listdir(SCRATCHDIR + "MULT/"):
            if file.endswith(".inp"):
                N += 1
        if N >= MULTMININP:
            run = "sbatch -N6 -c2 " + SCRATCHDIR + "MULT.sh " + "-i " + MULT + "/"
            os.system(run)


def WatchFresh():
    """
    Watch FRESH directory for new files. Adds new data to CSV file

    :return: None
    """
    for file in os.listdir(FRESHDIRPATH):
        if file.endswith(".inp"):
            filename = os.path.splitext(file)[0]
            f = open(FRESHDIRPATH + file, "r")
            datafile = f.read()
            f.close()

            theorylvl = "ERR"
            for _ in datafile:
                if PBE0 in datafile:
                    theorylvl = PBE0
                if MP2 in datafile:
                    theorylvl = MP2

            if theorylvl == "ERR":
                source = FRESHDIRPATH + file
                destin = FAILEDPATH + "BADINP/" + file
                os.rename(source, destin)
                continue

            if IsFileInCSV(filename):
                if GetValueCSV(filename, "Status") == ST_ERR:
                    ChangeValueCSV(filename, "TheoryLvl", theorylvl)
                    ChangeValueCSV(filename, "Errcode", 0)
                    continue
                else:
                    source = FRESHDIRPATH + file
                    destin = FAILEDPATH + "EXIST/" + file
                    os.rename(source, destin)
                    continue
            else:
                state = ST_FRESH
                element = GetHeavyAtom(datafile)
                multip = GetMpFromOrcaInp(datafile)
                AddLineCSV(filename, theorylvl, element, multip, state)


def WatchFromScratch():
    """
    Process all files that had been calculated already

    :return: None
    """
    FromQueueToProcessed(PBE0)
    FromQueueToProcessed(MP2)

    for file in os.listdir(FROMSCRATCHDIR):
        if file.endswith(".out"):
            filename = os.path.splitext(file)[0]
            f = open(FROMSCRATCHDIR + file, "r")
            datafile = f.read()
            f.close()

            status = GetOrcaOutStatus(datafile)
            if status == 1:  # HURRAY
                if GetValueCSV(filename, "TheoryLvl") == PBE0:
                    element = GetValueCSV(filename, "Element")
                    multip = GetValueCSV(filename, "Multip")
                    MakeInputFile(filename, MP2, element, 0, multip, GetOrcaOutXyz(FROMSCRATCHDIR + file))
                    ChangeValueCSV(filename, "TheoryLvl", MP2)
                    FromProcessedToQueue(filename, PBE0)
                    ChangeValueCSV(filename, "Status", ST_QUEUE)

                else:  # DONE
                    FromProcessedToDone(filename)
                    ChangeValueCSV(filename, "Status", ST_DONE)

            elif status == 2:  # Repeat
                element = GetValueCSV(filename, "Element")
                theorylvl = GetValueCSV(filename, "TheoryLvl")
                multip = GetValueCSV(filename, "Multip")
                MakeInputFile(filename, theorylvl, element, 0, multip, GetOrcaOutXyz(FROMSCRATCHDIR + file))
                FromProcessedToQueue(filename, PBE0)
                ChangeValueCSV(filename, "Status", ST_QUEUE)

            else:  # HOUSTON WE HAVE A PR...
                ChangeValueCSV(filename, "Status", ST_ERR)
                ChangeValueCSV(filename, "Errcode", status)
                theorylvl = GetValueCSV(filename, "TheoryLvl")
                FromProcessedToError(filename, theorylvl)


def WatchFreshToQueue():
    """
    Sends all fresh files to scratch

    :return: None
    """
    for file in os.listdir(FRESHDIRPATH):
        if file.endswith(".inp"):
            filename = os.path.splitext(file)[0]
            FromFreshToQueue(filename, GetValueCSV(filename, "TheoryLvl"))
            ChangeValueCSV(filename, "Status", ST_QUEUE)


def WatchDoneToMult():
    """
    If there's some done geoms - start search for the-best-multiplicity task

    :return: None
    """
    for file in os.listdir(MP2CONVGEDPATH):
        if file.endswith(".out"):
            filename = os.path.splitext(file)[0]
            xyz = GetOrcaOutXyz(filename)
            init_mult = GetValueCSV(filename, "Multip")

            for mult in range(init_mult+2, MAXMULTIP, 2):
                MakeInputFile(filename+"__"+mult, MULT, GetValueCSV(filename, "Element"), 0, mult, xyz)

            ChangeValueCSV(filename, "Status", ST_QUEUE)
            ChangeValueCSV(filename, "TheoryLvl", MULT)


def WatchMult():
    """
    Read multiplicities and get the best one

    :return: None
    """
    if IsInLomonosovSqueue(MULT):
        return

    Summary = []

    for file in os.listdir(SCRATCHDIR + "MULT/"):
        if file.endswith(".out"):
            filename = os.path.splitext(file)[0]
            filename = filename.split("__")

            f = open(file, "r")
            content = f.read()
            f.close()

            Summary.append([filename[0], filename[1], GetOrcaOutE(content)])

    for elem in Counter(Summary[0]).keys():
        mp = GetValueCSV(elem, "Multip")
        en = GetOrcaOutE(MP2CONVGEDPATH+elem+".out")
        Summary.append([elem, mp, en])

    Summary.sort(key=lambda x: x[0])

    minE = 0
    optMP = 0
    curF = ""

    for elem in Summary:
        if elem[0] != curF:
            if curF != "":
                ChangeValueCSV(curF, "Multip", optMP)
                ChangeValueCSV(curF, "Status", ST_MULT)
                source = FROMSCRATCHDIR + curF + ".gbw"
                destin = MP2CONVGEDPATH + curF + ".gbw"
                os.rename(source, destin)
            curF = elem[0]
            optMP = elem[1]
            minE = elem[2]
        elif elem[2] < minE:
            minE = elem[2]
            optMP = elem[1]

# End of module ALPWatchers

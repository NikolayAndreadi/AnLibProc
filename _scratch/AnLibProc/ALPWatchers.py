# ALPWatchers - module for target file processing

from ALPDelivery import *
from ALPOrcaIO import *


def WatchLomonosovScript():
    """
    If some files requires computation and script doesn't work - start it

    :return: None
    """
    if platform.system() == "Windows":
        return

    if not IsInLomonosovSqueue(PBE0):
        N = 0
        for file in os.listdir(SCRATCHDIR + "PBE0/"):
            if file.endswith(".inp"):
                N += 1
        if N >= PBE0MININP:
            run = "sbatch -N3 -t 48:00:00 " + SCRATCHDIR + "PBE0.sh -i" + SCRATCHDIR + "PBE0/"
            os.system(run)

    if not IsInLomonosovSqueue(MP2):
        N = 0
        for file in os.listdir(SCRATCHDIR + "MP2/"):
            if file.endswith(".inp"):
                N += 1
        if N >= MP2MININP:
            run = "sbatch -N6 -c2 " + SCRATCHDIR + "MP2.sh -i" + SCRATCHDIR + "MP2/"
            os.system(run)

    if not IsInLomonosovSqueue(MULT):
        N = 0
        for file in os.listdir(SCRATCHDIR + "MULT/"):
            if file.endswith(".inp"):
                N += 1
        if N >= MULTMININP:
            run = "sbatch -N6 -c2 " + SCRATCHDIR + "MULT.sh -i" + SCRATCHDIR + "MULT/"
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
                    ChangeValueCSV(filename, "Iter_num", 0)
                    continue
                else:
                    source = FRESHDIRPATH + file
                    destin = FAILEDPATH + "EXIST/" + file
                    os.rename(source, destin)
                    continue
            else:
                state = ST_FRESH
                element = GetHeavyAtom(datafile)
                multip = GetMpFromOrcaInp(datafile, 2)
                chg = GetMpFromOrcaInp(datafile, 1)
                AddLineCSV(filename, theorylvl, element, chg, multip, state)


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
                    charge = GetValueCSV(filename, "Charge")
                    MakeInputFile(filename, MP2, element, charge, multip, GetOrcaOutXyz(FROMSCRATCHDIR + file))
                    ChangeValueCSV(filename, "TheoryLvl", MP2)
                    FromProcessedToQueue(filename, MP2)
                    ChangeValueCSV(filename, "Status", ST_QUEUE)
                    ChangeValueCSV(filename, "Iter_num", 0)

                else:  # DONE
                    FromProcessedToDone(filename)
                    ChangeValueCSV(filename, "Status", ST_DONE)

            elif status == 2:  # Repeat
                element = GetValueCSV(filename, "Element")
                theorylvl = GetValueCSV(filename, "TheoryLvl")

                ChangeValueCSV(filename, "Iter_num", str(int(GetValueCSV(filename, "Iter_num")) + 1))

                if int(GetValueCSV(filename, "Iter_num")) > MAX_ITER:
                    ChangeValueCSV(filename, "Status", ST_ERR)
                    ChangeValueCSV(filename, "Errcode", "TooManyIterations")
                    theorylvl = GetValueCSV(filename, "TheoryLvl")
                    FromProcessedToError(filename, theorylvl)
                    continue

                multip = GetValueCSV(filename, "Multip")
                charge = GetValueCSV(filename, "Charge")
                MakeInputFile(filename, theorylvl, element, charge,
                              multip, GetOrcaOutXyz(FROMSCRATCHDIR + file), True)
                FromProcessedToQueue(filename, theorylvl)
                ChangeValueCSV(filename, "Status", ST_QUEUE)

            elif status == 5:  # create with HCore
                element = GetValueCSV(filename, "Element")
                theorylvl = GetValueCSV(filename, "TheoryLvl")
                charge = GetValueCSV(filename, "Charge")
                multip = GetValueCSV(filename, "Multip")
                MakeInputFile(filename, theorylvl, element, charge,
                              multip, GetOrcaOutXyz(FROMSCRATCHDIR + file), False)
                FromProcessedToQueue(filename, theorylvl)
                ChangeValueCSV(filename, "Status", ST_QUEUE)

            elif status == 4:  # wrong element, replace
                element = GetHeavyAtom(GetOrcaOutXyz(FROMSCRATCHDIR + file))
                multip = GetValueCSV(filename, "Multip")
                charge = GetValueCSV(filename, "Charge")
                tl = GetValueCSV(filename, "TheoryLvl")
                MakeInputFile(filename, tl, element, charge, multip, GetOrcaOutXyz(FROMSCRATCHDIR + file))
                FromProcessedToQueue(filename, tl)
                ChangeValueCSV(filename, "Status", ST_QUEUE)

            else:  # HOUSTON WE HAVE A PR...
                ChangeValueCSV(filename, "Status", ST_ERR)
                theorylvl = GetValueCSV(filename, "TheoryLvl")
                FromProcessedToError(filename, theorylvl, False)
                ChangeValueCSV(filename, "Iter_num", 0)

                if status == 0:
                    ChangeValueCSV(filename, "Errcode", "Unknown error")
                elif status == 3:
                    ChangeValueCSV(filename, "Errcode", "SCF not conv")
                elif status == 6:
                    ChangeValueCSV(filename, "Errcode", "CP-SCF not conv")
                elif status == 7:
                    ChangeValueCSV(filename, "Errcode", "Lambda eq not conv")
                elif status == 8:
                    ChangeValueCSV(filename, "Errcode", "Out of memory")


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
            xyz = GetOrcaOutXyz(MP2CONVGEDPATH+filename+".out")
            init_mult = GetValueCSV(filename, "Multip")
            charge = GetValueCSV(filename, "Charge")

            for mult in range(int(init_mult)+2, MAXMULTIP, 2):
                MakeInputFile(filename+"__"+str(mult), MULT, GetValueCSV(filename, "Element"),
                              charge, mult, xyz)

            ChangeValueCSV(filename, "Status", ST_QUEUE)
            ChangeValueCSV(filename, "TheoryLvl", MULT)


def WatchMult():
    """
    Read multiplicities and get the best one
    TODO: there is no check whether all multiplicities were calculated correctly (for one molecule)

    :return: None
    """
    if IsInLomonosovSqueue(MULT):
        return

    if not IsAnyTask(MULT):
        return

    Summary = []

    for file in os.listdir(SCRATCHDIR + "MULT/"):
        if file.endswith(".out"):
            filename = os.path.splitext(file)[0]
            filename = filename.split("__")

            f = open(SCRATCHDIR + "MULT/"+file, "r")
            content = f.read()
            f.close()

            Summary.append([filename[0], filename[1], GetOrcaOutE(content)[-1]])

    def get__column(matrix, i):
        return [row[i] for row in matrix]
    Summ_names = get__column(Summary, 0)
    Summ_names = list(dict.fromkeys(Summ_names))
    for elem in Summ_names:
        mp = GetValueCSV(elem, "Multip")
        f = open(MP2CONVGEDPATH + elem + ".out", "r")
        content = f.read()
        f.close()
        en = GetOrcaOutE(content)[-1]
        Summary.append([elem, mp, en])

    Summary.sort(key=lambda x: x[0])

    minE = 0
    optMP = 0
    curF = "Dev__none"

    for elem in Summary:
        if curF != elem[0]:
            if curF == "Dev__none":
                curF = elem[0]
                minE = elem[2]
                optMP = elem[1]
            else:
                ChangeValueCSV(curF, "Multip", optMP)
                ChangeValueCSV(curF, "Status", ST_MULT)
                source = FROMSCRATCHDIR + curF + ".gbw"
                if os.path.isfile(source):
                    destin = MP2CONVGEDPATH + curF + ".gbw"
                    os.rename(source, destin)
                curF = elem[0]
                minE = elem[2]
                optMP = elem[1]
        elif float(elem[2]) < float(minE):
            minE = elem[2]
            optMP = elem[1]

    ChangeValueCSV(curF, "Multip", optMP)
    ChangeValueCSV(curF, "Status", ST_MULT)

    source = FROMSCRATCHDIR + curF + ".gbw"
    if os.path.isfile(source):
        destin = MP2CONVGEDPATH + curF + ".gbw"
        os.rename(source, destin)

    for file in os.listdir(SCRATCHDIR + "MULT/"):
        if file != ".keep":
            os.remove(SCRATCHDIR + "MULT/" + file)

# End of module ALPWatchers

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
            run = "sbatch -N9 -c3 -t 72:00:00 " + SCRATCHDIR + "MP2.sh -i" + SCRATCHDIR + "MP2/"
            os.system(run)

    if not IsInLomonosovSqueue(MULT):
        N = 0
        for file in os.listdir(SCRATCHDIR + "MULT/"):
            if file.endswith(".inp"):
                N += 1
        if N >= MULTMININP:
            run = "sbatch -N6 -c2 -t 12:00:00 " + SCRATCHDIR + "MULT.sh -i" + SCRATCHDIR + "MULT/"
            os.system(run)

    if not IsInLomonosovSqueue(CC):
        N = 0
        for file in os.listdir(SCRATCHDIR + "CC/"):
            if file.endswith(".inp"):
                N += 1
        if N >= MULTMININP:
            run = "sbatch -N10 -c7 -t 72:00:00 " + SCRATCHDIR + "CC.sh -i" + SCRATCHDIR + "CC/"
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

            if PBE0 in datafile:
                theorylvl = PBE0
            elif MP2 in datafile:
                theorylvl = MP2
            elif "HF" in datafile:
                # HF is a default setting in gabedit editor. Change to PBE0 template
                theorylvl = PBE0
                xyz = GetOrcaInpXyz(datafile)
                heavyatom = GetHeavyAtom(xyz)
                cg = GetMpFromOrcaInp(datafile, 1)
                mp = GetMpFromOrcaInp(datafile, 2)
                MakeInputFile(filename, theorylvl, heavyatom, cg, mp, xyz, False, FRESHDIRPATH)

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
    FromQueueToProcessed(CC)

    for file in os.listdir(FROMSCRATCHDIR):
        print(file)
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
                tl = GetValueCSV(filename, "TheoryLvl")
                if element == 0:
                    ChangeValueCSV(filename, "Status", ST_ERR)
                    FromProcessedToError(filename, tl, False)
                    ChangeValueCSV(filename, "Iter_num", 0)
                    ChangeValueCSV(filename, "Errcode", "Bad element")
                    continue

                multip = GetValueCSV(filename, "Multip")
                charge = GetValueCSV(filename, "Charge")

                MakeInputFile(filename, tl, element, charge, multip, GetOrcaOutXyz(FROMSCRATCHDIR + file))
                FromProcessedToQueue(filename, tl)
                ChangeValueCSV(filename, "Status", ST_QUEUE)

            elif status == 666:  # CC task, the last check
                source = FROMSCRATCHDIR + filename + ".out"
                destin = CCCONVGEDPATH + filename + ".out"
                os.rename(source, destin)

                source = FROMSCRATCHDIR + filename + ".gbw"
                if os.path.isfile(source):
                    destin = CCCONVGEDPATH + filename + ".gbw"
                    os.rename(source, destin)

                ChangeValueCSV(filename, "Status", ST_CC)

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

            if GetValueCSV(filename, "TheoryLvl") == ST_MULT:
                continue
            if GetValueCSV(filename, "TheoryLvl") == ST_CC:
                continue

            xyz = GetOrcaOutXyz(MP2CONVGEDPATH + filename + ".out")
            init_mult = GetValueCSV(filename, "Multip")
            charge = GetValueCSV(filename, "Charge")

            for mult in range(int(init_mult) + 2, MAXMULTIP, 2):
                MakeInputFile(filename + "__" + str(mult), MULT, GetValueCSV(filename, "Element"),
                              charge, mult, xyz)

            ChangeValueCSV(filename, "Status", ST_QUEUE)
            ChangeValueCSV(filename, "TheoryLvl", MULT)


def WatchDoneToСС():
    """
    If there's some done geoms with mult - start coupled cluster task

    :return: None
    """
    for file in os.listdir(MP2CONVGEDPATH):
        if file.endswith(".out"):
            filename = os.path.splitext(file)[0]
            if GetValueCSV(filename, "TheoryLvl") == ST_MULT:
                xyz = GetOrcaOutXyz(MP2CONVGEDPATH + filename + ".out")
                mult = GetValueCSV(filename, "Multip")
                charge = GetValueCSV(filename, "Charge")
                MakeInputFile(filename, CC, GetValueCSV(filename, "Element"),
                              charge, mult, xyz)
                ChangeValueCSV(filename, "Status", ST_QUEUE)
                ChangeValueCSV(filename, "TheoryLvl", CC)

                f = MP2CONVGEDPATH + filename + ".gbw"
                if os.path.isfile(f):
                    destin = SCRATCHDIR + CC + '/' + filename + ".gbw"
                    os.rename(f, destin)


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

            f = open(SCRATCHDIR + "MULT/" + file, "r")
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

    print("Name\tMP\tEnergy")
    for elem in Summary:
        print(elem[0], elem[1], elem[2])

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
                ChangeValueCSV(curF, "TheoryLvl", ST_MULT)
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
    ChangeValueCSV(curF, "TheoryLvl", ST_MULT)

    source = FROMSCRATCHDIR + curF + ".gbw"
    if os.path.isfile(source):
        destin = MP2CONVGEDPATH + curF + ".gbw"
        os.rename(source, destin)

    for file in os.listdir(SCRATCHDIR + "MULT/"):
        if file.endswith(".out"):
            filename = os.path.splitext(file)[0] + ".inp"
            os.remove(SCRATCHDIR + "MULT/" + file)
            os.remove(SCRATCHDIR + "MULT/" + filename)

    for file in os.listdir(SCRATCHDIR + "MULT/"):
        if file != ".keep":
            if not file.endswith(".inp"):
                os.remove(SCRATCHDIR + "MULT/" + file)

# End of module ALPWatchers

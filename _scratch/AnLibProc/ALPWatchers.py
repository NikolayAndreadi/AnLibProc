from ALPCSV import *
from ALPDelivery import *
from ALPOrcaIO import *


# WatchLomonosovScript - if some files requires computation and script doesn't work - start it
def WatchLomonosovScript():
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


# WatchFresh - watch FRESH directory
# add new files to DATAFILE if not existed or corrected after error
def WatchFresh():
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


# process all that crap that poor FROMSCRATCH folder containes
def WatchFromScratch():
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


# WatchFreshToQueue - sends all fresh files to _scratch
def WatchFreshToQueue():
    for file in os.listdir(FRESHDIRPATH):
        if file.endswith(".inp"):
            filename = os.path.splitext(file)[0]
            FromFreshToQueue(filename, GetValueCSV(filename, "TheoryLvl"))
            ChangeValueCSV(filename, "Status", ST_QUEUE)

# End of module ALPWatchers

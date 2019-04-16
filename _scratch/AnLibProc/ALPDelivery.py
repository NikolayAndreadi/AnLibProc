import os
from ALPconstant import *
from ALPCSV import ChangeValueCSV
from subprocess import check_output


# FromFreshToQueue - accept all fresh files to queue
def FromFreshToQueue(fn, tl):
    source = FRESHDIRPATH + fn + ".inp"
    destin = SCRATCHDIR + tl + '/' + fn + ".inp"
    os.rename(source, destin)


# IsInLomonosovSqueue - returns true if orca script still running
def IsInLomonosovSqueue(tl):
    result = check_output(LOMSQUEUECMD, shell=True).decode('ascii')

    if result.find(tl) != -1:
        return True
    else:
        return False

    # FromQueueToProcessed


'''
This part is lilbit tricky:
We should watch for .inp, then find so-called.out for 
this .inp
We do it so 'cause timeout hurts our asses badly
So maybe some files not even begin to be calculated
Also check for .gbw, then cleanup
I'm not good with messing around CSV in Delivery, but it 
seems to be the shortest way to make things work
'''


def FromQueueToProcessed(tl):
    if IsInLomonosovSqueue(tl):
        return 0

    dirn = SCRATCHDIR + tl + '/'
    for file in os.listdir(dirn):
        if file.endswith(".inp"):
            filename = os.path.splitext(file)[0]
            outfile = dirn + filename + ".out"
            if os.path.isfile(outfile):
                destin = FROMSCRATCHDIR + filename + ".out"
                os.rename(outfile, destin)

                outfile = dirn + filename + ".gbw"
                if os.path.isfile(outfile):
                    destin = FROMSCRATCHDIR + filename + ".gbw"
                    os.rename(outfile, destin)

                ChangeValueCSV(filename, "Status", ST_COMPUTED)

                outfile = dirn + filename + ".inp"
                os.remove(outfile)

    for file in os.listdir(dirn):
        if not file.endswith(".inp"):
            os.remove(file)


# FromProcessedToDone - move out and gbw to DONE directory, put DONE flag
def FromProcessedToDone(fn):
    source = FROMSCRATCHDIR + fn + ".out"
    destin = MP2CONVGEDPATH + fn + ".out"
    os.rename(source, destin)

    source = FROMSCRATCHDIR + fn + ".gbw"
    if os.path.isfile(source):
        destin = MP2CONVGEDPATH + fn + ".gbw"
        os.rename(source, destin)


# It means we delete .out file and move .gbw to ToScratch
def FromProcessedToQueue(fn, tl):
    f = FROMSCRATCHDIR + fn + ".out"
    os.remove(f)
    f = FROMSCRATCHDIR + fn + ".gbw"
    if os.path.isfile(f):
        destin = SCRATCHDIR + tl + '/' + fn + ".gbw"
        os.rename(f, destin)


# If error occures, delete gbw file (seemes its broken already) and replace to err folder
def FromProcessedToError(fn, tl):
    source = FROMSCRATCHDIR + fn + ".out"
    destin = FAILEDPATH + tl + '/' + fn + ".out"
    os.rename(source, destin)

    source = FROMSCRATCHDIR + fn + ".gbw"
    if os.path.isfile(source):
        os.remove(source)

# End of module ALPDelivery

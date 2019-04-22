# ALPDelivery - module for file management

from ALPCSV import *
from ALPOrcaIO import *


def FromFreshToQueue(fn, tl):
    """
    Move all fresh files to queue (scratch directory)

    :param fn: filename
    :param tl: theory level
    :return: None
    """
    source = FRESHDIRPATH + fn + ".inp"
    destin = SCRATCHDIR + tl + '/' + fn + ".inp"
    os.rename(source, destin)


def IsInLomonosovSqueue(tl):
    """
    platform.system()
    Is script with some theory level still running

    :param tl: theory level
    :return: True if still running
    """
    return False


"""
    result = check_output(LOMSQUEUECMD, shell=True).decode('ascii')

    if result.find(tl) != -1:
        return True
    else:
        return False
"""

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
    """
    Move calculated files to script folder

    :param tl: theory level
    :return: None
    """
    if IsInLomonosovSqueue(tl):
        return

    dirn = SCRATCHDIR + tl + '/'
    for file in os.listdir(dirn):
        if file.endswith(".inp"):
            filename = os.path.splitext(file)[0]
            outfile = dirn + filename + ".out"

            f = open(dirn + file, "r")
            datafile = f.read()
            f.close()

            end_status = GetOrcaOutTaskStatus(datafile)

            if end_status > 1:
                element = GetValueCSV(filename, "Element")
                theorylvl = GetValueCSV(filename, "TheoryLvl")
                multip = GetValueCSV(filename, "Multip")
                os.remove(dirn + filename + ".inp")
                MakeInputFile(filename, theorylvl, element, 0, multip, GetOrcaOutXyz(dirn + file))

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


def FromProcessedToDone(fn):
    """
    Move files to DONE directory if MP2 geom opt task succeeded

    :param fn: filename
    :return: None
    """
    source = FROMSCRATCHDIR + fn + ".out"
    destin = MP2CONVGEDPATH + fn + ".out"
    os.rename(source, destin)


def FromProcessedToQueue(fn, tl):
    """
    Removes .out file and move .gbw to scratch directory. Used if geom opt is not succeeded.

    :param fn: filename
    :param tl: theory level
    :return: None
    """
    f = FROMSCRATCHDIR + fn + ".out"
    os.remove(f)
    f = FROMSCRATCHDIR + fn + ".gbw"
    if os.path.isfile(f):
        destin = SCRATCHDIR + tl + '/' + fn + ".gbw"
        os.rename(f, destin)


def FromProcessedToError(fn, tl):
    """
    If error occures, delete gbw file (seemes its broken already) and replace to err folder

    :param fn: filename
    :param tl: theory level
    :return: None
    """
    source = FROMSCRATCHDIR + fn + ".out"
    destin = FAILEDPATH + tl + '/' + fn + ".out"
    os.rename(source, destin)

    source = FROMSCRATCHDIR + fn + ".gbw"
    if os.path.isfile(source):
        os.remove(source)

# End of module ALPDelivery

# ALPCSV - module for processing CSV datafile

import os
import csv
from ALPconstant import *


def CreateCSV():
    """
    Creates CSV file where all mol props are contained

    :return: None
    """
    if not os.path.isfile(DATAPATH):
        with open(DATAPATH, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSVHEADER)
            writer.writeheader()


def AddLineCSV(fn, tl, el, mp, st, err=0, iter_num=0):
    """
    Adding new task info to CSV

    :param fn: filename
    :param tl: theory level
    :param el: heavy element
    :param mp: multiplicity
    :param st: state
    :param err: error code
    :param iter_num: retry number of iterations
    :return: None
    """
    with open(DATAPATH, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([fn, tl, el, mp, st, err, iter_num])


def GetValueCSV(fn, field):
    """
    Get field value from CSV

    :param fn: filename whose value we want to extract
    :param field: parameter whose value we want to extract
    :return: value of parameter for this filename
    """
    with open(DATAPATH, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["Filename"] == fn:
                return row[field]


# ChangeValueCSV - change some FIELD value to VALUE for FILENAME
def ChangeValueCSV(fn, field, value):
    """
    Change some field value to new for some filename

    :param fn: filename whose value we want to change
    :param field: what parameter we want to change
    :param value: new value
    :return: None
    """
    with open(DATAPATH, 'r') as csvfile:
        reader = csv.reader(csvfile)
        lines = list(reader)

        for i in lines:
            if i[CSVHEADER.index("Filename")] == fn:
                i[CSVHEADER.index(field)] = value

    with open(DATAPATH, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerows(lines)


def IsFileInCSV(fn):
    """
    Checks if file is already in CSV

    :param fn: filename we want to check
    :return: True if already in CSV
    """
    with open(DATAPATH, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["Filename"] == fn:
                return True
        return False


def IsAnyTask(tl):
    """
    Is task with theory level exists

    :param tl: Theory level
    :return: True if exists
    """
    with open(DATAPATH, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["TheoryLvl"] == tl:
                return True
        return False

# End of module ALPCSV

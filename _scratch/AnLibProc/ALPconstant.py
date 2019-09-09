# ALPconstant - module with all required constants: paths, names, etc.

import platform

# where datafile exists
DATAPATH = "./DATA/Data.csv"

# directory to place new .inp
FRESHDIRPATH = "./FILES/1.FRESH/"

# directory for ready-to-run inputs
if platform.system() == "Windows":
    SCRATCHDIR = "../"
else:
    SCRATCHDIR = "/home/nikolayandreadi_2125/_scratch/"

FROMSCRATCHDIR = "./FILES/2.FromScratch/"
FAILEDPATH = "./FILES/3.Failed/"
MP2CONVGEDPATH = "./FILES/4.Done-MP2/"
CCCONVGEDPATH = "./FILES/5.Done-CC/"

# field names in CSV
CSVHEADER = ["Filename", "TheoryLvl", "Element", "Charge",
             "Multip", "Status", "Errcode", "Iter_num"]

# list of heavy elements
HEAVYLIST = ["Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf"]

# Theory levels. Just for saving time
PBE0 = "PBE0"
MP2 = "MP2"
MULT = "MULT"
CC = "CC"

# Check orca out statuses:
# return 0 if unknoun problem
STATUS = {
    1: "HURRAY",
    2: "The optimization did not converge but reached",
    3: "SCF NOT CONVERGED AFTER",
    4: "There are no main   basis functions on atom number",
    5: "Error encountered when trying to calculate the atomic fitting density!",
    6: "THE CP-SCF CALCULATION IS UNCONVERGED",
    7: "The lambda equations have not converged",
    8: "OUT OF MEMORY ERROR",
    666: "CCSD(T)"
}

"""
STATES CONSTANTS
"""
# flag for new files or files after error correction
ST_FRESH = "FRESH"
# flag for inputs that ready for calculations
ST_QUEUE = "QUEUE"
# if computation complete
ST_COMPUTED = "COMPUTED"
# if untrivial error occures
ST_ERR = "ERR"
# when MP2 calculation done
ST_DONE = "DONE"
# when target multiplicity is found out
ST_MULT = "DONE+MULT"
#last step
ST_CC = "DONE+CC"

# min files needed for script to run
PBE0MININP = 1
MP2MININP = 1
MULTMININP = 2
CCMININP = 1

# max multiplicity for mp-search task
MAXMULTIP = 7

# max iteration number
MAX_ITER = 3

# SQUEUE LOMONOSOV SHELL COMMAND
LOMSQUEUECMD = "squeue -u nikolayandreadi_2125"

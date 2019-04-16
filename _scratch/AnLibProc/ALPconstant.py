# ALPconstant - module with all required constants: paths, names, etc.

# where datafile exists
DATAPATH = "./DATA/Data.csv"

# directory to place new .inp
FRESHDIRPATH = "./FILES/1.FRESH/"

# directory for ready-to-run inputs
SCRATCHDIR = "/home/nikolayandreadi_1705/_scratch/"
FROMSCRATCHDIR = "./FILES/2.FromScratch/"
FAILEDPATH = "./FILES/3.Failed/"
MP2CONVGEDPATH = "./FILES/4.Done-MP2/"

# field names in CSV
CSVHEADER = ["Filename", "TheoryLvl", "Element", "Multip", "Status", "Errcode"]

# list of heavy elements
HEAVYLIST = ["Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf"]

# Theory levels. Just for saving time and butt
PBE0 = "PBE0"
MP2 = "MP2"
MULT = "MULT"

# Check orca out statuses:
# return 0 if unknoun problem
STATUS = {
    1: "HURRAY",
    2: "The optimization did not converge but reached",
    3: "SCF NOT CONVERGED AFTER"
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
ST_MULT = "DONE+"

# min files needed for script to run
PBE0MININP = 1
MP2MININP = 1

# SQUEUE LOMONOSOV SHELL COMMAND
LOMSQUEUECMD = "squeue -u nikolayandreadi_1705"

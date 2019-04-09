#ALPCSV - module for processing CSV datafile

import os, csv
from ALPconstant import *

#CreateCSV - generating datafile if not exists
def CreateCSV():
	if not os.path.isfile(DATAPATH):
		with open(DATAPATH, 'w', newline='') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames = CSVHEADER)
			writer.writeheader()

#AddLineCSV - adding new file info to CSV
def AddLineCSV(fn, tl, el, mp, st, err=0):
	with open(DATAPATH, 'a', newline='') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow([fn,tl,el,mp,st,err])
		
#GetValueCSV - get FIELD value by FILENAME
def GetValueCSV(fn,field):
	with open(DATAPATH, 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if row["Filename"] == fn:
				return row[field]

#ChangeValueCSV - change some FIELD value to VALUE for FILENAME
def ChangeValueCSV (fn, field, value):
	with open(DATAPATH, 'r') as csvfile:
		reader = csv.reader(csvfile)
		lines =list(reader)
		
		for i in lines:
			if i[CSVHEADER.index("Filename")] == fn:
				i[CSVHEADER.index(field)] = value
				
	with open(DATAPATH, 'w', newline='') as csvfile:
		writer = csv.writer(csvfile, delimiter = ',')
		writer.writerows(lines)
	
#IsFileInCSV - returns true if FILENAME is already in datafile	
def IsFileInCSV(fn):
	with open(DATAPATH, 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if row["Filename"] == fn:
				return True
		return False

#End of module ALPCSV
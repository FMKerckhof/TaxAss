###############################################################################
# find_seqIDs_blast_removed.py
# Copyright (c) 2016, Joshua J Hamilton, Robin R Rohwer, and Katherine D McMahon
# Affiliation: Department of Bacteriology
#              University of Wisconsin-Madison, Madison, Wisconsin, USA
# URL: http://http://mcmahonlab.wisc.edu/
# All rights reserved.
################################################################################
# This script creates a list of all the seqIDs in the specified fasta file.
# Then it creates a list of all the seqIDs in in the specified blast.table file.
# The script then identifies all seqIDs missing from the blast.table file and
# appends them to the below-cutoff seqID file generated by the R script 
# filter_seqIDs_by_pident.R.
#
# The format for typing into the terminal is:
# $ python fetch_seqIDs_blast_removed.py fastaFile blastFile outputFile
# where 	fetch_seqIDs_blast_removed.py		path to this script
#		fastaFile						path to the fasta file containing all the seqIDs
#		blastFile						path to the blast results in table format (col1 = seqID)				
#		outputFile						path to the file with below-cutoff seqID file generated by the R script find_seqIDs_with_pident.R

#%%#############################################################################
### Import packages
################################################################################
from Bio import SeqIO
import os
import sys

#%%#############################################################################
### Read input arguments from command line into variable names
################################################################################
fastaFile = sys.argv[1]
blastFile = sys.argv[2]
outputFile = sys.argv[3]

#%%#############################################################################
### Process the list of all seqIDs in fastaFile and identify those missing from
### the BLAST output
################################################################################

# Create hash of all SeqIDs in fasta file
allIDs = {}
fileHandle = open(fastaFile)
for record in SeqIO.parse(fileHandle, "fasta") :
    allIDs[record.id] = None
fileHandle.close()
    
# Create List of all SeqIDs in blast output file
blastIDs = {}
with open(blastFile) as blast:
    for line in blast:
        blastIDs[line.split()[0]] = None

# Find seqIDs that are missing in blast and append them to the missing IDs output file
for key in allIDs:
    if key not in blastIDs:
        with open(outputFile,"a") as missing :
            missing.write(key + "\n")

# Close all the files you've opened
blast.close()
missing.close()
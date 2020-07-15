#! /usr/bin/env python
####################################################################
#combine_mpa.py converts multiple outputs from kreport2mpa.py
#Copyright (C) 2020 Jennifer Lu, jennifer.lu717@gmail.com

#This file is part of KrakenTools.
#KrakenTools is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 3 of the license, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of 
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, see <http://www.gnu.org/licenses/>.

####################################################################
#Jennifer Lu, jlu26@jhmi.edu
#Updated: 07/12/2020
#
#This program reads multiple files in the 
#an mpa-format (MetaPhlAn) style report (as output from kreport2mpa.py).
#Each line represents a possible taxon classification. The first column is lists the 
#domain, kingdom, phyla, etc, leading up to each taxon.
#The levels are separated by the | delimiter, with the type of 
#level specified before each name with a single letter and underscore
#(d_ for domain, k_ for kingdom, etc). 
#The second column is the number of reads classified within 
#that taxon's subtree.
#
#Input files:
#   - MetaPhlAn format (mpa-format) files with two columns 
#   - All files must be generated from the same database, with the same
#     options from kreport2krona.py or errors may occur
#     
#Input Parameters to Specify [OPTIONAL]:
#   - header_line = prints a header line in mpa-report 
#       [Default: no header]
#   - intermediate-ranks = includes non-traditional taxon levels
#       (traditional levels: domain, kingdom, phylum, class, order, 
#       family, genus, species)
#       [Default: no intermediate ranks]
#Output file format (tab-delimited)
#   - Taxonomy tree levels |-delimited, with level type [d,k,p,c,o,f,g,s,x]
#   - Number of reads within subtree of the specified level
#
#Methods
#   - main
#
import os, sys, argparse

#Main method
def main():
    #Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True,
        nargs='+', dest='in_files',
        help='Input files for this program (files generated by kreport2mpa.py)')
    parser.add_argument('-o', '--output', required=True,
        dest='o_file', help='Single mpa-report file name')
    args=parser.parse_args()

    #Process each file 
    samples = {} #Map number to name
    sample_count = 0 
    values = {} #Map taxon tree to sample to number 
    parent2child = {}
    toparse = []
    sys.stdout.write(" Number of files to parse: %i\n" % len(args.in_files))
    for in_file in args.in_files:
        i_file = open(in_file,'r')
        sample_count += 1
        sample_name = "Sample #" + str(sample_count) 
        for line in i_file:
            #Check for header line 
            if line[0] == "#":
                sample_name = line.strip().split('\t')[-1]
                continue 
            #Otherwise
            [classification, val] = line.strip().split('\t')
            #Check for parents
            split_vals = classification.split("|")
            curr_parent = ''
            for i in range(0,len(split_vals)):
                test_val = "|".join(split_vals[0:i]) 
                if test_val in values: 
                    curr_parent = test_val 
            #No parent
            if curr_parent == '':
                if classification not in values:
                    toparse.append(classification) 
            #Most specific parent found 
            if curr_parent != '':
                if curr_parent not in parent2child:
                    parent2child[curr_parent] = []
                if classification not in parent2child[curr_parent]:
                    parent2child[curr_parent].append(classification)
            #Save classification to value map
            if classification not in values:
                values[classification] = {}
            values[classification][sample_count] = val
        #Save sample name 
        samples[sample_count] = sample_name 
    
    sys.stdout.write(" Number of classifications to write: %i\n" % len(values))
    sys.stdout.write("\t%i classifications printed" % 0)
    #Write header
    o_file = open(args.o_file, 'w')
    o_file.write("#Classification") 
    for i in range(1, sample_count+1):
        o_file.write("\t" + samples[i])
    o_file.write("\n") 
    
    #Write each line  
    parsed = {} 
    count_c = 0 
    while len(toparse) > 0:
        curr_c = toparse.pop(0)
        #Add all children to stack 
        if curr_c in parent2child: 
            for child in parent2child[curr_c]: 
                toparse.insert(0, child) 
        #For the current classification, print per sample
        o_file.write(curr_c) 
        for i in range(1,sample_count + 1):
            if i in values[curr_c]:
                o_file.write("\t" + values[curr_c][i])
            else:
                o_file.write("\t0")
        o_file.write("\n")
        count_c += 1
        sys.stdout.write("\r\t%i classifications printed" % count_c)
        sys.stdout.flush()
    o_file.close() 
    sys.stdout.write("\r\t%i classifications printed\n" % count_c)
    sys.stdout.flush()

if __name__ == "__main__":
    main()

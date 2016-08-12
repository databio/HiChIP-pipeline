#!/usr/bin/env python

#file_in="GM_cohesin_repeatmask_merge_allValidPairs"
#file_out="GM_cohesin_repeatmask_merge_allValidPairs_pre.txt"

from __future__ import print_function
from argparse import ArgumentParser

import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

parser = ArgumentParser(description='Formatter')

parser.add_argument('-i', '--input', required=True, 
					dest = 'infile',type=str, help='genome size for Macs2')

args = parser.parse_args()


i=1
j=2

interactions = []

for line in open(args.infile):
	line=line.strip().split()
	str1 = line[3]
	str2 = line[6]
	if str1=="+":
		str1="0"
	if str2=="+":
		str2="0"
	if str1=="-":
		str1="1"
	if str2=="-":
		str2="1"

	chr1 = line[1].replace("chr", "")
	chr2 = line[4].replace("chr", "")

	if chr1 > chr2:
		interaction_string = "-".join([chr1, chr2])
	else:
		interaction_string = "-".join([chr2, chr1])
	try:
		index = interactions.index(interaction_string)
		#eprint(index, interaction_string)
	except ValueError:  # Index not found
		interactions.append(interaction_string)
		index = len(interactions) -1
		eprint(index, interaction_string)

	print_line = "\t".join([str(i), str(str1), str(chr1), str(line[2]), str(i), str(str2),
	 str(chr2), line[5], str(j), str(30), str(31), str(index)])
	print(print_line)
	#print(str(i) + "\t" + str(str1) + "\t" + str(chr1[3:]) + "\t" + str(line[2]) + "\t" + str(i) + "\t" + str(str2) + "\t" + str(chr2[3:]) + "\t" + line[5] + "\t" 
#+ str(j) + "\t" + str(30) + "\t" + str(31) + "\t" + str(index) + "\n")
	i = i+1
	j = j+1	


#out.close()

#10 123186
# 4 157052397
#59940935
#60017012
#HWI-J00104_BSF_0239:6:1222:27742:29026#HiChIP1s3_A673sh_DSG_H3K27ac_S15890/1	chr10	123186	-	chr4	157052397	-	NA	NA	NA	42	42	

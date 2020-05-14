import tabula
import numpy as np
import re
import math
import pandas as pd
import os
import sys
import argparse

#TODO change argument types from str to relevant types
#TODO add flags instead of inputs
parser = argparse.ArgumentParser(description=
                                 'Tool to visualize raw table data')
parser.add_argument('File', type=str, help='File path of datasheet')
parser.add_argument('Pages', type=str, help='Pages to scrape')
parser.add_argument('Stream', type=str, 
                    help='Tables not seperated by lines')
parser.add_argument('Lattice', type=str,
                    help='Tables seperated by lines')
parser.add_argument('Guess', type=str, help='Guess area of table')
parser.add_argument('Area', type=str, help='Area boundaries of table')

args = parser.parse_args()

gss = None
a = None
strm = None
lttc = None
if args.Guess == 'True':
  gss = True
if args.Area != 'None':
  a = args.Area.split(',')
if args.Stream == 'True':
  strm = True
if args.Lattice == 'True':
  lttc = True

result = tabula.read_pdf(args.File, pages = args.Pages, area = a, 
                         guess = gss, stream = strm, lattice = lttc)

for i in range(len(result)):
  print('================================================================')
  print('Table Number: ' + str(i) + '\n')
  print()
  print(result[i])
  print()
  print('================================================================')


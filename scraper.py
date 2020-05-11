import tabula
import numpy as np
import re
import math
import pandas as pd
import string
import os
import sys
import argparse

# Component Package
# mpn - manufacturer part number
# size - number of pins
class package:
  def __init__(self, mpn, size):
    self.mpn = mpn
    self.size = size
    self.pins ={}
    self.maxNameLen = len('Ref') 
    self.maxNumLen = len('Int ...')

  def addPin(self, name, number):
    self.maxNameLen = max(self.maxNameLen, len(name))
    self.maxNumLen = max(self.maxNumLen, len(number))
    self.pins[number] = pin(name, number)
    

  def __str__(self):
    result = ['[' + align_text(self.maxNameLen, 'Ref') + '|' +
              align_text(self.maxNumLen, 'Int ...') + ']']
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', 
                                                             key)]
    for key in sorted(self.pins.keys(), key = alphanum_key):
      result = result + ['[' + 
               align_text(self.maxNameLen, self.pins[key].name) + '|' +
               align_text(self.maxNumLen, self.pins[key].number) + ']'] 
    return '\n'.join(result)

# Pin
# name - pin name
# number - pin number
class pin:
  def __init__(self, name, number):
      self.name = name
      self.number = number

  def __str__(self):
      return '[ ' + self.name + ' | ' + self.number + ' ]\n'

# Aligns the text in the associated PinSpec column
# maxlen - length of longest string in the PinSpec column
# text - text to be added to column
def align_text(maxlen, text):
    return ' ' + text + ((maxlen - len(text)) * ' ') + ' '

# Scrapes a datasheet for the name and number of pins associated with a 
# package. 
# pkgName - package name
# pkgSize - number of pins in package
# fName - path to datasheet file
# pgs - pages where pin description tables are located
# strm - [True, False, None] - stream mode for when tables are
#                              not seperated by lines
# lttc - [True, False, None] - lattice mode for when tables are
#                              seperated by lines
# gss - [True, False, None] - guess area of table on the page
# a - [y1, x1, y2, x2] or None : y1 = top of table
#                                x1 = left of table
#                                y2 = top + height of table
#                                x2 = left + width of table
# numCol - column number of column containing pin numbers
# nameCol - column number of column containing pin names
# tableNums - list of table numbers from DataFrame containing pin data
def scrape(pkgName, pkgSize, fName, pgs, strm, lttc, gss, a, numCol, 
           nameCol, tableNums):
  result = package(pkgName, pkgSize)
  for n in tableNums:
    table_vals = tabula.read_pdf(fName, area = a, guess = gss, pages = pgs,
                                 stream = strm, lattice = lttc)[n]
    height, width = table_vals.shape
    #TODO Figure out if we need to add epad
    for i in range(height):
      name = nameFilter(str(repr(table_vals.iat[i,nameCol])))
      numbers = numFilter(str(repr(table_vals.iat[i,numCol])))
      for n in numbers:
        result.addPin(name, n)
  return result

# Filters pin number string from table
# number - string data for pin numbers
def numFilter(number):
  number = number.replace('\'', '')
  number = number.replace('\\r', '')
  number = number.replace(' ', '')
  raw = [number] 
  result = []
  if re.search(',', number):
    raw = number.split(',')
  for n in raw:
    if re.search('^[0-9]{1,2}.[0-9]{1,3}$', n):
      result.append(str(int(float(n))))  
    elif re.search('^[A-Z]?[0-9]{1,2}$', n):
      result.append(n)
  return result 

# Filters pin name string from table
# name - string data for pin names
def nameFilter(name):
  name = name.replace('\'', '')
  name = name.replace('\\r', '')
  return name

# Prints a package's PinSpec to a file
# package - instance of package that will be printed
def toFile(package):
  f = open('./pins.txt', 'w+')
  f.write(str(package))

parser = argparse.ArgumentParser(description= 'Scrape pinSpec for component package')
parser.add_argument('Component', type=str, 
                    help='Name of Specific Component')
args = parser.parse_args()

pkg = None

# ========================================================================
# SUPPORTED COMPONENTS
# ========================================================================
if args.Component == 'adm7150':
  pkg = scrape('ADM7150', 8, 'datasheets/ADM7150.pdf', '6-6', True, 
                  None, None, [271.9575, 32.5125, 447.1425, 133.4925], 0,
                  1, [0])
elif args.Component == 'cc2640_rgz':
  pkg = scrape('CC2640-RGZ', 48, 'datasheets/cc2640.pdf', '7-8', None, 
                  True, None, None, 1, 0, [3, 4]) 
elif args.Component == 'cc2640_rhb':
  pkg = scrape('CC2640-RHB', 32, 'datasheets/cc2640.pdf', '9-10', None,
                  True, None, None, 1, 0, [3, 4]) 
elif args.Component == 'cc2640_rsm':
  pkg = scrape('CC2640-RSM', 32, 'datasheets/cc2640.pdf', '11-12', 
                  None, True, None, None, 1, 0, [3, 4]) 
elif args.Component == 'stm32l433_lqfp48': 
  pkg = scrape('STM32L433_LQFP48', 48, 'datasheets/stm32l433rc.pdf', 
                  '61-73', None, True, None, None, 0, 9, 
                  [i for i in range(1, 26)]) 
elif args.Component == 'stm32l433_ufbga100':
  pkg = scrape('STM32L433_UFBGA100', 100, 'datasheets/stm32l433rc.pdf',
                  '61-73', None, True, None, None, 8, 9, 
                  [i for i in range(1, 26)]) 

# ========================================================================

print(pkg)
toFile(pkg)

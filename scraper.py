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
# p - parameters 
class package:
  def __init__(self, p):
    self.params = p
    self.mpn = p.pkgName 
    self.size = p.pkgSize 
    self.pins = {}
    self.maxNameLen = len('Ref') 
    self.maxNumLen = len('Int ...')
    self.maxTypeLen = len('Type ...')
    self.maxDirLen = len('Dir  ')
    self.printType = p.printType 
    self.pinDir = p.pinDir

  def addPin(self, name, number, pinType):
    self.maxNameLen = max(self.maxNameLen, len(name))
    self.maxNumLen = max(self.maxNumLen, len(number))
    if pinType:
      self.maxTypeLen = max(self.maxTypeLen, len(pinType))
    self.pins[number] = pin(name, number, pinType)
    
  def joinPins(self):
    temp = {}
    result = {}
    maxNumLen = self.maxNumLen
    for p in self.pins.values():
      if p.name in temp:
        temp[p.name][0].append(p.number)
      else:
        temp[p.name] = ([p.number], p.pinType)
    for name in temp.keys():
      numbers = ' '.join(temp[name][0])
      maxNumLen = max(maxNumLen, len(numbers))
      result[numbers] = pin(name, numbers, temp[name][1])
    return (result, maxNumLen)

  def __str__(self):
    (joinedPins, maxNumLen) = self.joinPins()
    result = []
    if len(joinedPins) > 0:
      testNum = next(iter(joinedPins.values())).number
      header = '[' + align_text(self.maxNameLen, 'Ref') + '|'
      if re.search('^[A-Z]+', testNum) :
        header += align_text(self.maxNumLen, 'Ref ...') + '|'
      else:
        header += align_text(maxNumLen, 'Int ...') + '|'
      if self.printType:
        header += align_text(self.maxTypeLen, 'Type ...') + '|'
      header += align_text(self.maxDirLen, 'Dir  ') + ']'
      result.append(header)
    for key in sorted(joinedPins, key = lambda key: joinedPins[key].name) :
      row = '[' + align_text(self.maxNameLen, joinedPins[key].name) + '|' 
      row += align_text(maxNumLen, joinedPins[key].number) + '|'
      if self.printType:
        row += align_text(self.maxTypeLen, joinedPins[key].pinType) + '|' 
      row += align_text(self.maxDirLen, self.pin_dir(joinedPins[key])) + ']'
      result.append(row)
    return '\n'.join(result)


  # Solves for pin direction
  # p - pin
  # returns pin direction 
  def pin_dir(self, p):
    if not self.pinDir:
      if p.pinType == 'Power':
        return 'Down'
      if p.pinType == 'I/O':
        return 'Left'
      if p.pinType == 'Input':
        return 'Right'
      return 'Left'
    else:
      return self.pinDir 

# Aligns the text in the associated PinSpec column
# maxlen - length of longest string in the PinSpec column
# text - text to be added to column
# returns aligned text for column
def align_text(maxlen, text):
  return ' ' + text + ((maxlen - len(text)) * ' ') + ' '
      
# Pin
# name - pin name
# number - pin number
class pin:
  def __init__(self, name, number, pinType):
      self.name = name
      self.number = number
      self.pinType = pinType 

# Scrapes a datasheet for the name and number of pins associated with a 
# package. 
def scrape(p): 
  pkg = package(p)
  for n in p.tableNums:
    if p.strm:
      p.lttc = False
    table_vals = tabula.read_pdf(p.fName, area = p.a, guess = p.gss, 
                                 pages = p.pgs, stream = p.strm, 
                                 lattice = p.lttc)[n]
    height, width = table_vals.shape
    #TODO Figure out if we need to add epad
    for i in range(height):
      name = nameFilter(str(repr(table_vals.iat[i, p.nameCol])))
      numbers = numFilter(str(repr(table_vals.iat[i, p.numCol])))
      typeName = None 
      if p.typeCol:
        typeName = str(repr(table_vals.iat[i, p.typeCol]))
        typeName = typeFilter(typeName, name) 
      else:
        typeName = typeFilter(None, name)
      for n in numbers:
        pkg.addPin(name, n, typeName)
  return pkg 
 
# Parameters to scrape function
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
# typeCol - column number of column containing pin types
# printType - include pin type in PinSpec
# pinDir - inputs = ['Up', 'Down', 'Left', 'Down', None]
#        - direction of pins on symbol
#        - Input None automatically solves based on pin names
# tableNums - list of table numbers from DataFrame containing pin data
class scrapeParams:
  def __init__(self):
    self.pkgName = None
    self.pkgSize = None
    self.fName = None 
    self.tableNums = None
    self.numCol = None
    self.nameCol = None
    self.typeCol = None
    self.pgs = 'all' 
    self.strm = None 
    self.lttc = True 
    self.gss = None 
    self.a = None
    self.printType = True
    self.pinDir = None 

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
    if re.search('^[0-9]+.[0-9]+$', n):
      result.append(str(int(float(n))))  
    elif re.search('^[0-9]+$', n):
      result.append(n)
    elif re.search('^[A-Z]+[0-9]{1,2}$', n):
      result.append(n[:1] + '[' + n[1:] + ']')
  return result 

# Filters pin name string from table
# name - string data for pin names
def nameFilter(name):
  name = name.replace('\'', '')
  name = name.replace('\\r', '')
  return name

# Filters pin type string from table
# pinType - string data for pin type
# name    - pin name
# typeCol - is pin type column provided in datasheet? 
def typeFilter(typeName, name):
  if not typeName:
    if re.search('^[vV]+', name):
      return 'Power'
    else:
      return 'Misc'
  power = ['Power', 'power', 'S']
  io = ['I/O'] 
  i = ['input', 'I', 'i']
  typeName = typeName.replace('\'', '')
  typeName = typeName.replace('\\r', '')
  for s in power:
    if s in typeName:
      return 'Power'
  for s in io:
    if s in typeName:
      return 'I/O'
  for s in i:
    if s in typeName:
      return 'Input'
  return None 

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

params = scrapeParams()
success = True
# ========================================================================
# SUPPORTED COMPONENTS
# ========================================================================
if args.Component == 'adm7150':
  params.pkgName = 'ADM7150' 
  params.pkgSize = 8
  params.fName = 'datasheets/ADM7150.pdf' 
  params.tableNums = [0] 
  params.pgs = '6-6'
  params.strm = True 
  params.a = [271.9575, 32.5125, 447.1425, 133.4925]
  params.numCol = 0 
  params.nameCol = 1 

elif args.Component == 'cc2640_rgz':
  params.pkgName = 'CC2640-RGZ' 
  params.pkgSize = 48 
  params.fName = 'datasheets/cc2640.pdf' 
  params.tableNums = [3, 4] 
  params.pgs = '7-8' 
  params.numCol = 1 
  params.nameCol = 0 
  params.typeCol = 2 

elif args.Component == 'cc2640_rhb':
  params.pkgName = 'CC2640-RHB' 
  params.pkgSize = 32 
  params.fName = 'datasheets/cc2640.pdf' 
  params.tableNums = [3, 4] 
  params.pgs = '9-10' 
  params.numCol = 1 
  params.nameCol = 0 
  params.typeCol = 2 

elif args.Component == 'cc2640_rsm':
  params.pkgName = 'CC2640-RSM' 
  params.pkgSize = 32 
  params.fName = 'datasheets/cc2640.pdf' 
  params.tableNums = [3, 4] 
  params.pgs = '11-12' 
  params.numCol = 1 
  params.nameCol = 0 
  params.typeCol = 2 

elif args.Component == 'stm32l433_lqfp48': 
  params.pkgName = 'STM32L433_LQFP48'
  params.pkgSize = 48
  params.fName = 'datasheets/stm32l433rc.pdf' 
  params.tableNums = [i for i in range(1, 26)] 
  params.pgs = '61-73' 
  params.numCol = 0 
  params.nameCol = 9 
  params.typeCol = 10 

elif args.Component == 'stm32l433_ufqfpn48': 
  params.pkgName = 'STM32L433_UFQFPN48'
  params.pkgSize = 48
  params.fName = 'datasheets/stm32l433rc.pdf' 
  params.tableNums = [i for i in range(1, 26)] 
  params.pgs = '61-73' 
  params.numCol = 1 
  params.nameCol = 9 
  params.typeCol = 10 

elif args.Component == 'stm32l433_wlcsp49': 
  params.pkgName = 'STM32L433_WLCSP49'
  params.pkgSize = 49
  params.fName = 'datasheets/stm32l433rc.pdf' 
  params.tableNums = [i for i in range(1, 26)] 
  params.pgs = '61-73' 
  params.numCol = 2 
  params.nameCol = 9 
  params.typeCol = 10 

elif args.Component == 'stm32l433_wlcsp64': 
  params.pkgName = 'STM32L433_WLCSP64'
  params.pkgSize = 64 
  params.fName = 'datasheets/stm32l433rc.pdf' 
  params.tableNums = [i for i in range(1, 26)] 
  params.pgs = '61-73' 
  params.numCol = 3 
  params.nameCol = 9 
  params.typeCol = 10 

elif args.Component == 'stm32l433_lqfp64': 
  params.pkgName = 'STM32L433_LQFP64'
  params.pkgSize = 64 
  params.fName = 'datasheets/stm32l433rc.pdf' 
  params.tableNums = [i for i in range(1, 26)] 
  params.pgs = '61-73' 
  params.numCol = 4 
  params.nameCol = 9 
  params.typeCol = 10 

elif args.Component == 'stm32l433_lqfp64_smps': 
  params.pkgName = 'STM32L433_LQFP64_SMPS'
  params.pkgSize = 64 
  params.fName = 'datasheets/stm32l433rc.pdf' 
  params.tableNums = [i for i in range(1, 26)] 
  params.pgs = '61-73' 
  params.numCol = 5 
  params.nameCol = 9 
  params.typeCol = 10 

elif args.Component == 'stm32l433_ufbga64': 
  params.pkgName = 'STM32L433_UFBGA64'
  params.pkgSize = 64 
  params.fName = 'datasheets/stm32l433rc.pdf' 
  params.tableNums = [i for i in range(1, 26)] 
  params.pgs = '61-73' 
  params.numCol = 6 
  params.nameCol = 9 
  params.typeCol = 10 

elif args.Component == 'stm32l433_lqfp100': 
  params.pkgName = 'STM32L433_lqfp100'
  params.pkgSize = 100 
  params.fName = 'datasheets/stm32l433rc.pdf' 
  params.tableNums = [i for i in range(1, 26)] 
  params.pgs = '61-73' 
  params.numCol = 7 
  params.nameCol = 9 
  params.typeCol = 10 

elif args.Component == 'stm32l433_ufbga100':
  params.pkgName = 'STM32L433_ufbga100'
  params.pkgSize = 100 
  params.fName = 'datasheets/stm32l433rc.pdf' 
  params.tableNums = [i for i in range(1, 26)] 
  params.pgs = '61-73' 
  params.numCol = 8 
  params.nameCol = 9 
  params.typeCol = 10 

else:
  success = False
  print("Package Not Supported Yet")

#========================================================================
if success:
  pkg = scrape(params)
  print(pkg)
  toFile(pkg)

import tabula
import numpy
import re
import math

def hasNumbers(inputString):
  return bool(re.search(r'\d', inputString))

class procPin:
  def __init__(self, pinNum, pinName, pinFuncs):
    self.pinNum = pinNum
    self.pinName = pinName
    self.pinFuncs = pinFuncs
  def print_fn(self):
    return '`'+ self.pinName + ' => ' + self.pinNum + '\n'

pf = tabula.read_pdf("https://www.st.com/resource/en/datasheet/stm32l433rc.pdf", pages = '62-73', lattice = True)
pf = pf.values.astype(str)
# Collect list of all unique functions

# Per package, create list of pins, list of pins available for each function
lqfp = pf[:,4].tolist()
idx = [i for i, s in enumerate(lqfp) if hasNumbers(s)] # Get indexes
pins = []
fl = []
for i in idx:
  pStr = pf[i,9].split('\r')[0]
  pStr = pStr.split('-')[0]
  pStr = pStr.split('/')[0]
  funcs = pf[i,-1].split(',') + pf[i,-2].split(',')
  funcs = [x for x in funcs if not ('-' in x)]
  funcs = [x.replace('\r', '').strip() for x in funcs]
  fl = fl + funcs
  out = procPin(pf[i,4], pStr, funcs)
  pins.append(out)

# Unique, alphebetized list of functions
fl = sorted(list(set(fl)), key=str.lower)

# Find pins matching functions
pinByFunc = []
for f in fl:
  pinByFunc.append([p.pinName for p in pins if f in p.pinFuncs])

f = open('./pins', 'w+')
for p in pins:
  f.write(p.print_fn())
f.write('\n\n')
for l,p in zip(fl,pinByFunc):
  s = l + ' -- ' + ''.join([i +', ' for i in p]) + '\n'
  f.write(s)

f.close()


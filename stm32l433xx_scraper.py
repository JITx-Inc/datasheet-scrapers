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

pf = tabula.read_pdf("https://www.st.com/resource/en/datasheet/stm32l433rc.pdf", pages = '62-73', lattice = True)
pf = pf.values.astype(str)
# Collect list of all unique functions

# Per package, create list of pins, list of pins available for each function
lqfp = pf[:,4].tolist()
idx = [i for i, s in enumerate(lqfp) if hasNumbers(s)] # Get indexes
pins = []
for i in idx:
  pStr = pf[i,9].split('\r')[0]
  pStr = pStr.split('-')[0]
  pStr = pStr.split('/')[0]
  funcs = pf[i,-1].split(',\r') + pf[i,-2].split(',\r')
  funcs = [x for x in funcs if not ('-' in x)]
  out = procPin(pf[i,4], pStr, funcs)
  pins.append(out)



import tabula
import numpy
import re
import math


pf = tabula.read_pdf("datasheets/stm32l433rc.pdf", pages = '62-73', lattice = True)

print(pf)
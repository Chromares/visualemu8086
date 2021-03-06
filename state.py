import func
from func import *
import ctypes
import sys
from table import *
c_uint8 = ctypes.c_uint8

# Objects defining registers and segment registers

class Flags_bits(ctypes.LittleEndianStructure):
    _fields_ = [
    		("reserved_15", c_uint8, 1),
    		("I/O_Privilege_b_0", c_uint8, 1),
    		("I/O_Privilege_b_1", c_uint8, 1),
    		("Nested_f", c_uint8, 1),
		("overflow", c_uint8, 1),
		("direction", c_uint8, 1),
		("interrupt", c_uint8, 1),
		("trap", c_uint8, 1),
		("sign", c_uint8, 1),
		("zero", c_uint8, 1),
		("reserved_5", c_uint8, 1),
		("ac", c_uint8, 1),
		("reserved_3", c_uint8, 1),
		("parity", c_uint8, 1),
		("reserved_1", c_uint8, 1),
		("carry", c_uint8, 1),	
        ]
        
class Flags(ctypes.Union):
    _fields_ = [("b", Flags_bits),
                ("asbyte", c_uint8)]

class var_8(object):
	name = ""
	def __init__(self):
		self.val = 00
	def update(self):
		if(self.val > 255):
			while(self.val > 255):
				self.val -= 256
			flags.b.carry = 1
			flags.b.sign = 0
			flags.b.zero = 0
		elif(self.val < 0):
			flags.b.sign = 1
			flags.b.carry = 0
			flags.b.zero = 0
			self.val += 256
		elif(self.val == 0):
			flags.b.zero = 1
			flags.b.sign = 0
			flags.b.carry = 0	#sign, zero, carry, parity | overflow
		c = 0
		temp = self.val
		while (temp > 0):
			if(temp & 1 == 1):
				c = c + 1
			temp = temp >> 1
		if(c % 2 == 0 and c != 0):
			flags.b.parity = 1
		else:
			flags.b.parity = 0
class var_16(object):
	name = ""
	def __init__(self):
		self.val = 0000
	def update(self):
		if(self.val > 65535):
			while(self.val > 65535):
				self.val -= 65536
			flags.b.carry = 1
			flags.b.sign = 0
			flags.b.zero = 0
		elif(self.val < 0):
			self.val += 65536		#store in 2'sc?
			flags.b.carry = 0
			flags.b.sign = 1
			flags.b.zero = 0
		elif(self.val == 0):
			flags.b.carry = 0
			flags.b.sign = 0
			flags.b.zero = 1
		c = 0
		temp = self.val
		while (temp > 0):
			if(temp & 1 == 1):
				c = c + 1
			temp = temp >> 1
		if(c % 2 == 0 and c != 0):
			flags.b.parity = 1
		else:
			flags.b.parity = 0		

class special_var(object):
	name = ""
	def __init__(self, order):
		self.val = 0000
		self.order = order
	def update(self):		
		#self.val = int(hex(reg[self.order].val)[2:] + hex(reg[self.order + 1].val)[2:], 16)
		if(reg[self.order].val < 16):
			a = '0' + hex(reg[self.order].val)[2:]
		else:
			a = hex(reg[self.order].val)[2:]
		if(reg[self.order + 1].val < 16):
			b = '0' + hex(reg[self.order + 1].val)[2:] 
		else:
			b = hex(reg[self.order + 1].val)[2:]
		self.val = int(a + b, 16)				
	def valoverride(self, value):
		self.val = value
		if(self.val > 0):
			while(self.val > 65535):
				self.val -= 65536
			flags.b.carry = 1
			flags.b.sign = 0
			flags.b.zero = 0
		elif(self.val < 0):
			self.val += 65536
			flags.b.carry = 0
			flags.b.sign = 1
			flags.b.zero = 0
		elif(self.val == 0):
			flags.b.carry = 0
			flags.b.sign = 0
			flags.b.zero = 1
		c = 0
		temp = self.val
		while (temp > 0):
			if(temp & 1 == 1):
				c = c + 1
			temp = temp >> 1
		if(c % 2 == 0 and c != 0):
			flags.b.parity = 1
		else:
			flags.b.parity = 0
		if(self.val > 255):
			reg[self.order].val = int(hex(self.val)[2:-2], 16)
			reg[self.order + 1].val = int(hex(self.val)[-2:], 16)
		else:
			reg[self.order].val = 0
			reg[self.order + 1].val = self.val

class passer(object):
	def __init__(self):
		self.model = ''
		self.code = False
		self.data = False
		self.stack = -1
		self.lcount = 0

ipass = passer()
#CREATING Instances for each variable
ah = var_8()
ah.name = "ah"
al = var_8()
al.name = "al"
bh = var_8()
bh.name = "bh"
bl = var_8()
bl.name = "bl"
ch = var_8()
ch.name = "ch"
cl = var_8()
cl.name = "cl"
dh = var_8()
dh.name = "dh"
dl = var_8()
dl.name = "dl"
di = var_16()
di.name = "di"
si = var_16()
si.name = "si"
bp = var_16()
bp.name = "bp"
sp = var_16()
sp.name = "sp"
ds = var_16()
ds.name = "ds"
es = var_16()
es.name = "es"
ss = var_16()
ss.name = "ss"
cs = var_16()
cs.name = "cs"
virgin =  var_8()
virgin.name = "virgin"
ax = special_var(1)
ax.name = "ax"
bx = special_var(3)
bx.name = "bx"
cx = special_var(5)
cx.name = "cx"
dx = special_var(7)
dx.name = "dx"

flags = Flags()
flags.asbyte = 0x0
#flags.b.I/O_Privilege_b_0 = 
flags.b.Nested_f = 1
flags.b.reserved_15 = 1

					#      p   p                               p
reg = [virgin, ah, al, bh, bl, ch, cl, dh, dl, di, si, bp, sp, ds, es, ss, cs, ax, bx, cx, dx]
#	0       1   2  3   4   5   6   7   8   9   10  11  12  13  14  15  16  17  18  19   20

from bitstring import BitString
import sys
import re

REGISTERS = ("zero", "sp", "a0", "a1", "rr", "ra", "t0", "t1", "t2",
	"t3", "t4", "t5", "t6", "t7", "t8", "t9", "pc")

INSTRUCTIONS = ("add", "addi", "and", "eq", "jal", "jeq", "ori", "lui",
	"lw", "or", "sll", "srl", "sra", "slt", "sw", "sub")

labels = {}
temp = []

def uncomment(line):
	return str.strip(re.match(r"(.+)/{2}.*|(.*)", line).group(0))

def check_label(line, line_number):
	if line.endswith(":"):
		labels[line[:-1]] = line_number
		return False
	return True

def unpack(line):
	return re.findall("([^#,\s\(\)]+)", line)


index = 0
lines = []
for line in sys.stdin:
	line = uncomment(line)
	if line and check_label(line, index):
		lines.append(line)
		index += 1

for line in lines:
	unpacked = unpack(line)
	bits_left = 16

	if re.match("lw|sw", line):
		unpacked = [unpacked[0], unpacked[1], unpacked[3], unpacked[2]]
	elif re.match("jal|jeq", line):
		unpacked = [unpacked[0], labels[unpacked[1]]]
	
	bitline = ""
	while len(unpacked) > 0:
		item = unpacked.pop(0)
		if item in INSTRUCTIONS:
			bitline += BitString(uint = INSTRUCTIONS.index(item), length = 4).bin
			bits_left -= 4
		elif item in REGISTERS:
			bitline += BitString(uint = REGISTERS.index(item), length = 4).bin
			bits_left -= 4
		elif item in labels:
			bitline += BitString(int = labels[item], length = bits_left).bin
		else:
			bitline += BitString(int = int(item), length = bits_left).bin
			bits_left -= bits_left
			
	temp.append(bitline)

for index, line in enumerate(temp):
	sys.stdout.write(lines[index] + " // " + line + "\n")
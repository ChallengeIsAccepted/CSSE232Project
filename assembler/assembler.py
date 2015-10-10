from bitstring import BitString
import sys
import re

# We will use these tuples to contain an ordered collection or registers/instructions - their index corresponds to their bit value
REGISTERS = ("zero", "sp", "a0", "a1", "rr", "ra", "t0", "t1", "t2",
	"t3", "t4", "t5", "t6", "t7", "t8", "pc")

INSTRUCTIONS = ("add", "addi", "and", "eq", "jal", "jeq", "ori", "lui",
	"lw", "or", "sll", "srl", "sra", "slt", "sw", "sub")

# Used to hold any labels and their associated locations in the program
labels = {}

# Used to hold the translated binary until we can print it to stdout
temp = []

# Removes comments and extra whitespace from a line
def uncomment(line):
	return str.strip(re.match("([^/]*)", line).group(0))

# If we end with a colon, it's a label; add the label to the labels dictionary
def check_label(line, line_number):
	if line.endswith(":"):
		labels[line[:-1]] = line_number
		return False
	return True

# Turn an instruction into a list of each part (e.g. "sw #a0, 4(#sp)" = ['sw', 'a0', '4', 'sp'])
def unpack(line):
	return re.findall("([^#,\s\(\)]+)", line)

# Keeps track of the line that we're at: doesn't count labels, comments, or nil lines
index = 0

# Contains the assembly lines
lines = []

# Here we filter out anything not relevant and check for labels, then we stick the rest in the lines list
for line in sys.stdin:
	uline = uncomment(line)
	if uline and check_label(uline, index):
		lines.append(uline)
		index += 1

# This is where the magic happens
for line in lines:

	unpacked = unpack(line)
	
	# How many bits we have left in the line
	bits_left = 16

	# lw/sw and jql/jeq have to be reordered in order to match the other assembly commands
	if re.match("lw|sw", line):
		unpacked = [unpacked[0], unpacked[1], unpacked[3], unpacked[2]]
	elif re.match("jal|jeq", line):
		unpacked = [unpacked[0], labels[unpacked[1]]]
	
	# Contains the raw bits of the assembly
	bitline = ""

	# handles instructions, registers, labels, and immediates differently
	while bits_left > 0:
		if len(unpacked) == 0:
			bitline += "0000 "
			bits_left -= 4
			continue
		item = unpacked.pop(0)
		if item in INSTRUCTIONS:
			bitline += BitString(uint = INSTRUCTIONS.index(item), length = 4).bin + " "
			bits_left -= 4
		elif item in REGISTERS:
			bitline += BitString(uint = REGISTERS.index(item), length = 4).bin + " "
			bits_left -= 4
		elif item in labels:
			# shouldn't be necessary, but eventually we might want labels for immediate values (e.g. A = 1)
			bitline += BitString(int = labels[item], length = bits_left).bin + " "
			bits_left -= bits_left
		else:
			bitline += BitString(int = int(item), length = bits_left).bin
			bits_left -= bits_left
			
	temp.append(bitline)

# Now we just print it out
for index, line in enumerate(temp):
	sys.stdout.write(lines[index] + " // " + line + "\n")
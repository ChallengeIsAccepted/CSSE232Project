from bitstring import BitString
import sys
import re

# Used to hold any labels and their associated locations in the program
labels = {}

# Used to hold the translated binary until we can print it to stdout
machine_code = []

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

class Handler:
	def __init__(self):
		pass
	def __getitem__(self, item):
		return getattr(self, item)

	# This tuple corresponds to the registers available for use - their index is translated into their bit value
	REGISTERS = ("zero", "sp", "a0", "a1", "rr", "ra", "t0", "t1", "t2",
		"t3", "t4", "t5", "t6", "t7", "imm", "eq_reg")

	# This dictionary holds the instructions for us and separates them by category
	# Instruction types:
	# 	R = | OP = 4 | REG0 = 4 | REG1 = 4 | REG2 = 4 |
	#	I = | OP = 4 | REG0 = 4 |       IMM = 8       |
	#	S = | OP = 4 | REG0 = 4 | REG1 = 4 | IMM = 4  |
	#	J = | OP = 4 |            IMM = 12            |

	INSTRUCTIONS = {
		"R": {"add":0,"and":2,"eq":3,"or":9,"slt":13,"sub":15, "jmp":6},
		"I": {"seti":1,"lui":7,"sll":10,"srl":11,"sra":12},
		"J": {"jal":4,"jeq":5},
		"S": {"lw":8,"sw":14}
	}

	def handle_instruction(self, line):
		unpacked = unpack(line)
		for t in self.INSTRUCTIONS:
			if unpacked[0] in self.INSTRUCTIONS[t]:
				return self[t](unpacked)
		return "xxxx xxxx xxxx xxxx"

	def tobin(self, item, length):
		if item in self.REGISTERS:
			return BitString(uint = self.REGISTERS.index(item), length = length).bin
		elif re.match("-", item):
			return BitString(int = int(item), length = length).bin
		elif item.isdigit():
			return BitString(uint = int(item), length = length).bin
		elif item in labels:
			return BitString(uint = int(labels[item]), length = length).bin
		else:
			for t in self.INSTRUCTIONS:
				if item in self.INSTRUCTIONS[t]:
					return BitString(uint = self.INSTRUCTIONS[t][item], length = length).bin

		return "xxxx"

	def R(self, unpacked):
		bitline = ""
		for i in (0, 3, 1, 2):
			if i < len(unpacked):
				bitline += self.tobin(unpacked[i], 4) + " "
			else:
				bitline += "0000 "
		return str.strip(bitline)

	def I(self, unpacked):
		bitline = self.tobin(unpacked[0], 4) + " " + self.tobin(unpacked[1], 4) + " " + self.tobin(unpacked[2], 8)
		return bitline
	def J(self, unpacked):
		bitline = self.tobin(unpacked[0], 4) + " " + self.tobin(unpacked[1], 12)
		return bitline
	def S(self, unpacked):
		return self.R(unpacked)

handler = Handler()
for line in lines:
	machine_code.append(handler.handle_instruction(line))

# Now we just print it out
longest = len(max(lines, key = len)) + 7

for index, line in enumerate(machine_code):
	line_out = lines[index].ljust(longest) + "// " + line + "\n"
	sys.stdout.write(line_out)
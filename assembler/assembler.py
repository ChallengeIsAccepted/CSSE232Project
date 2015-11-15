import sys
import re

# Used to hold any labels and their associated locations in the program
labels = {}

# Used to hold the translated binary until we can print it to stdout
machine_code = []

# Keeps track of the line that we're at: doesn't count labels, comments, or nil lines
index = 0

# Contains the assembly lines
lines = []

REGISTERS = ["zero", "sp", "a0", "a1", "rr", "ra", "t0",
             "t1", "t2", "t3", "t4", "t5", "t6", "display", "imm", "eq_reg"]


def to_hex(s):
    return hex(int(s)).split("x")[1]


def build_instruction_handler(op, instr_type):
    def handler(items):
        s = "0x" + to_hex(op)
        if instr_type == "r":  # OP | reg2 | reg0 | reg1
            s += to_hex(REGISTERS.index(items[1]))
            s += to_hex(REGISTERS.index(items[2]))
            s += to_hex(REGISTERS.index(items[3]))
        elif instr_type == "i":  # OP | reg0 | imm
            s += to_hex(REGISTERS.index(items[1]))
            s += to_hex(items[2]).zfill(2)
        elif instr_type == "j":  # OP | imm
            s += to_hex(labels[items[1]]).zfill(3)
        elif instr_type == "z":  # OP | reg0 | 0 | 0
            s += to_hex(REGISTERS.index(items[1]))
            s += "00"
        elif instr_type == "s":  # OP | reg0 | reg1 | imm
            # Note that this is the weird one, because lw/sw
            s += to_hex(REGISTERS.index(items[1]))
            s += to_hex(REGISTERS.index(items[2]))
            s += to_hex(items[3])
        else:
            print("Invalid instruction type : " + instr_type)
            return "INVALID"

        return s

    def wrapper(items):
        try:
            return handler(items)
        except Exception:
            print("Failed to interpret command: " + items[0])
            return "!!!!"

    return wrapper


INSTRUCTIONS = {
    "add" : build_instruction_handler(0, "r"),
    "seti": build_instruction_handler(1, "i"),
    "and" : build_instruction_handler(2, "r"),
    "eq"  : build_instruction_handler(3, "r"),
    "jal" : build_instruction_handler(4, "j"),
    "jeq" : build_instruction_handler(5, "j"),
    "jmp" : build_instruction_handler(6, "z"),
    "lui" : build_instruction_handler(7, "i"),
    "lw"  : build_instruction_handler(8, "s"),
    "or"  : build_instruction_handler(9, "r"),
    "sll" : build_instruction_handler(10, "i"),
    "srl" : build_instruction_handler(11, "i"),
    "sra" : build_instruction_handler(12, "i"),
    "slt" : build_instruction_handler(13, "r"),
    "sw"  : build_instruction_handler(14, "s"),
    "sub" : build_instruction_handler(15, "r")
}


# Removes comments and extra whitespace from a line
def uncomment(s):
    return str.strip(re.match("([^/]*)", s).group(0))


# If we end with a colon, it's a label; add the label to the labels dictionary
def check_label(s, line_number):
    if s.endswith(":"):
        labels[s[:-1]] = line_number
        return False
    return True


# Turn an instruction into a list of each part (e.g. "sw #a0, 4(#sp)" = ['sw', 'a0', '4', 'sp'])
def unpack(s):
    return re.findall("([^#,\s\(\)]+)", s)


# Here we filter out anything not relevant and check for labels, then we stick the rest in the lines list
for line in sys.stdin:
    uline = uncomment(line)
    if uline and check_label(uline, index):
        lines.append(uline)
        index += 1

for line in lines:
    unpacked = unpack(line)
    machine_code.append(INSTRUCTIONS[unpacked[0]](unpacked))

# Now we just print it out
longest = len(max(lines, key=len)) + 7

for index, line in enumerate(machine_code):
    line_out = lines[index].ljust(longest) + "// " + line + "\n"
    sys.stdout.write(line_out)

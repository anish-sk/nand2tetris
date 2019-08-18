#!/usr/bin/python
import sys, os


def binary_arithmetic(command):
  operator = arithmetic_operators.get(command[0], command[0] + "not found ")
  assign = "M=M" + operator + "D\n"
  return popD + getM + assign

def unary_arithmetic(command):
  operator = arithmetic_operators.get(command[0], command[0] + "not found ")
  assign = "M=" + mathOp + "M\n"
  return getM + assign

def conditional(command):
  global ALabelnum

  if command[0] == "gt":
    name = "@ALabel_" + str(ALabelnum)
    test = "@" + name + "\nD;JGT\n"
    
  if command[0] == "eq":
    name = "@ALabel_e" + str(ALabelnum)
    test = "@" + name + "\nD;JEQ\n"
    
  if command[0] == "lt":
    name = "@ALabel_" + str(ALabelnum)
    test = "@" + name + "\nD;JLT\n"
    
  ALabelnum+=2
  label = "(" + name + ")\n"

  return popD + getM + diffTrue + test + makeFalse + label


def pushFun(command):
  segment = command[1]
  index = command[2]

  if segment == "constant":
    value = "@" + index + "\nD=A\n"
  elif segment == "static":
    value = "@" + fileName + "." + index + "\nD=M\n"
  else:
    if segment == "temp" or segment == "pointer":
      tpA = "A"
    else:
      tpA = "M"
    pointer = segment_code.get(segment, "invalid segment: " + segment + "\n")
    indexD = "@" + index + "\nD=A\n"
    valueD = "@" + pointer + "\nA=" + tpA + "+D\nD=M\n"
    value = indexD + valueD

  return value + push

def popFun(command):
  segment = command[1]
  index = command[2]

  if segment == "static":
    pointer = "@" + fileName + "." + index + "\n"
    return popD + pointer + "M=D\n"
  
  if segment == "temp" or segment == "pointer":
    tpA = "A"
  else:
    tpA = "M"
  pointer = segment_code.get(segment, "invalid segment: " + segment + "\n")
  indexD = "@" + index + "\nD=A\n"
  addressR13 = "@" + pointer + "\nD=" + tpA + "+D\n@R13\nM=D\n"
  change = "@R13\nA=M\nM=D\n"

  return indexD + addressR13 + popD + change


def initialize(file):
  file.write("\n///  " + file.name + " ///\n\n") 


def translate(line):
  command = line.split('/')[0].strip().split()
  if command == []:
    return ''
  else:
    f = translations.get(command[0], lambda x: "\n// Whoops!  " + command[0] + " not found\n\n")
    return f(command)
  

def main():
  arg = sys.argv[1]
  infiles = []

  if os.path.isfile(arg):
    path = os.path.dirname(arg)
    base = os.path.basename(arg)[:-3]
    infiles.append(base + ".vm") 
  elif os.path.isdir(arg):
    path = arg
    base = os.path.basename(arg)
    for file in os.listdir(arg):
      if file[-3:] == ".vm":
        infiles.append(file)

  outfile = open(os.path.join(path, base) + ".asm", "w")
  initialize(outfile)

  for f in infiles:
    global fileName 
    fileName = f[:-3]
    outfile.write("\n// translating " + f + " //\n\n")
    infile = open(os.path.join(path, f))
    for line in infile:
      outfile.write(translate(line))
    

translations = {
    "add": binary_arithmetic,
    "sub": binary_arithmetic,
    "or" : binary_arithmetic,
    "and": binary_arithmetic,
    "neg": unary_arithmetic,
    "not": unary_arithmetic,
    "eq" : conditional,
    "gt" : conditional,
    "lt" : conditional,
    "push" : pushFun,
    "pop"  : popFun,
    }

ALabelnum=0
popD = "@SP\nAM=M-1\nD=M\n"
getM = "@SP\nA=M-1\n"
diffTrue = "D=M-D\nM=-1\n"
makeFalse = "@SP\nA=M-1\nM=0\n"
push = "@SP\nA=M\nM=D\n@SP\nM=M+1\n"

arithmetic_operators = {
    "sub" : "-",
    "add" : "+",
    "and" : "&",
    "or"  : "|",
    "neg" : "-",
    "not" : "!",
    }

segment_code = {
    "argument" : "ARG",
    "this" : "THIS",
    "that" : "THAT",
    "local" : "LCL",
    "temp" : "5",
    "pointer" : "3"
    }



if __name__ == "__main__":
  main()


import sys, os

ALabelnum = 0

popD = "@SP\nAM=M-1\nD=M\n"
getM = "@SP\nA=M-1\n"
diffTrue = "D=M-D\nM=-1\n"
makeFalse = "@SP\nA=M-1\nM=0\n"
push = "@SP\nA=M\nM=D\n@SP\nM=M+1\n"

arithmetic_operators={
    "sub" : "-",
    "add" : "+",
    "and" : "&",
    "or" : "|",
    "neg" : "-",
    "not" : "!"
}

segment_code={
    "argument" : "ARG",
    "this" : "THIS",
    "that" : "THAT",
    "local" : "LCL",
    "temp" : "5",
    "pointer" : "3",
}
def unary_arithmetic(command):
    operator = arithmetic_operators.get(command[0],command[0]+"not found")
    assign = "M=" + operator + "M\n"
    return getM + assign

def binary_arithmetic(command):
    operator = arithmetic_operators.get(command[0],command[0]+"not found")
    assign = "M=M" + operator + "D\n"
    return popD + getM + assign

def conditional(command):
    global ALabelnum
    name ="ALabel_" + str(ALabelnum)
    if command[0] == "gt":        
        test = "@" + name + "\nD;JGT\n"
    if command[0] == "eq":        
        test = "@" + name + "\nD;JEQ\n"
    if command[0] == "lt":        
        test = "@" + name + "\nD;JLT\n"
    ALabelnum+=1
    label ="(" + name + ")\n"
    return popD + getM + diffTrue + test + makeFalse + label

def pushfunction(command):
    segment = command[1]
    index = command[2]
    if segment == "constant":
        value = "@" + index + "\nD=A\n"
    elif segment == "static":
        value = "@" + fileName + "." + index + "\nD=M\n"
    else:
        if segment == "temp" or segment == "pointer":
            tempp ="A"
        else:
            tempp ="M"
        pointer = segment_code.get(segment, "invalid segment: "+ segment + "\n")
        indexD ="@"+ index +"\nD=A\n"
        valueD ="@"+ pointer +"\nA=" + tempp + "+D\nD=M\n"
        value = indexD + valueD 
    return value + push

def popfunction(command):
    segment = command[1]
    index = command[2]
    if segment == "constant":
        raise Exception("you cannot pop into a constant")
    if segment == "static":
        pointer = "@" + fileName + "." + index + "\n"
        return popD + pointer + "M=D\n"
    if segment == "temp" or segment == "pointer":
        tempp="A"
    else:
        tempp="M"
    pointer = segment_code.get(segment, "invalid segment: "+ segment + "\n")
    indexD = "@" + index + "\nD=A\n"
    addressR13 = "@" + pointer + "\nD=" + tempp + "+D\n@R13\nM=D\n"
    change = "@R13\nA=M\nM=D\n"
    return indexD + addressR13 + popD + change

translations ={
    "add": binary_arithmetic,
    "sub": binary_arithmetic,
    "and": binary_arithmetic,
    "or": binary_arithmetic,
    "neg": unary_arithmetic,
    "not": unary_arithmetic,
    "eq": conditional,
    "gt": conditional,
    "lt": conditional,
    "push": pushfunction,
    "pop": popfunction
}

def initialize(file):
    file.write("\n///" + file.name + " ///\n")

def translate(line):
    command = line.split('/')[0].strip().split()
    if command == []:
        return ''
    else:
        f = translations.get(command[0], lambda x: "\n//Error: " + command[0] + " not found \n\n")
        return f(command)

def main():
    arg = sys.argv[1]
    global fileName 
    fileName = os.path.basename(arg)[:-3]
    infile = open(arg + ".vm")    
    outfile = open(arg + ".asm", "w")
    initialize(outfile)
    for line in infile:
        outfile.write(translate(line))

if __name__=="__main__":
    main()
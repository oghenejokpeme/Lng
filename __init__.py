import sys
import os

from parser import parse
from interpreter import Interpreter

def read_file(fileInput):
    read = os.read(fileInput, 4096)
    os.close(fileInput)

    return read

def entry_point(argv):
    try:
        filename = argv[1]
    except IndexError:
        print "Input file required!"
        return 1

    #Run program
    source = ''
    source += read_file(os.open(filename, os.O_RDONLY, 0777))
    ast = parse(source)

    ctx = Interpreter()
    ast.eval(ctx)
    #print ctx.env
    #print ctx.func_list

    return 0

def target(*args):
    return entry_point, None

if __name__ ==  "__main__":
    entry_point(sys.argv)
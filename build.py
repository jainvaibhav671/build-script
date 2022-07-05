#!/usr/bin/python3
import sys
import os
import getopt
from re import sub

from tomlkit import dumps
from tomlkit import parse
from tomlkit import table

def readConfig():
    home = os.environ.get('HOME')
    with open(os.path.join(f"{home}/.config","build.toml"), 'r') as f:
        doc = parse(f.read())
    return doc

def saveConfig(doc):
    with open(os.path.join("~/.config","build.toml"), 'w') as f:
        f.write(doc.dumps())


def getArgs():
    shortopt = ['-r', '-b', '-d']
    args = getopt.getopt(sys.argv, shortopts=shortopt)[1]

    if (len(args) < 3):
        print("Need arguments")
        sys.exit()

    args[2] = os.path.abspath(args[2])
    args[2] = os.path.basename(args[2])

    return args[1:]

def getcmd(file, mode, doc):
    modes = {
            "-b" : "build",
            "-r" : "run",
            "-d" : "delete"
    }
    mode = modes[mode]
    ext = os.path.splitext(file)[1][1:]
    if (ext == 'out'):
        return "./$1"
        
    if (not doc.get(ext)):
        return ""
    if (not doc.get(ext).get(mode)):
        return ""
    return doc.get(ext).get(mode)

def run(file, doc):
    mode = '-r'
    cmd = getcmd(file, mode, doc)
    
    if (len(cmd) == 0):
        return

    cmd = sub(r'\$1', file, cmd)
    state = os.system(cmd)
    if (state != 0):
        print("ERROR!")
        sys.exit()
    
def build(file, doc):
    mode = '-b'
    cmd = getcmd(file, mode, doc)

    if (len(cmd) == 0):
        return ""

    # $1 -> input file
    # $2 -> output file

    filename = os.path.splitext(file)[0]
    cmd = sub(r'\$1', file, cmd)
    cmd = sub(r'\$2', filename+'.out', cmd)
    state = os.system(cmd)
    if (state != 0):
        print("ERROR!")
        sys.exit()
    return filename+".out"

def delete(file):
    state = os.system(f"rm {file}")
    if (state != 0):
        print("ERROR!")
        sys.exit()

def main():
    doc = readConfig()
    mode, file = getArgs()

    if mode == '-b':
        f = build(file, doc)
        if (not f):
            print("Can't build")

    elif mode == '-r':
        f = build(file, doc)
        
        if len(f) == 0:
            run(file, doc)
        else:
            run(f, doc)

    elif mode == '-d':
        f = build(file, doc)
        if (not f):
            print("Can't build")
            sys.exit()
        run(f, doc)
        delete(f)

    print("\nFinished")

if __name__ == "__main__":
    main()



#!/usr/bin/python3
import sys
import os
import getopt
import subprocess as subp
from re import sub

from tomlkit import dumps
from tomlkit import parse
from tomlkit import table

class Builder:
    def __init__(self):
        self.doc = self.readConfig()
        self.mode, self.file = self.getArgs()

    def main(self):
        if self.mode == '-b':
            f = self.build()
            if (len(f) == 0):
                print("Can't build")
                sys.exit()
        elif self.mode == '-r':
            f = build()
            if (len(f) != 0):
                self.file = f
            self.run()
        elif self.mode == '-d':
            f = build();
            if (len(f) != 0):
                self.file = f
            self.run()
            self.delete()

    def readConfig(self):
        home = os.environ.get('HOME')
        with open(os.path.join(f"{home}/.config","build.toml"), 'r') as f:
            self.doc = parse(f.read())
        return self.doc

    def saveConfig(self):
        with open(os.path.join("~/.config","build.toml"), 'w') as f:
            f.write(self.doc.dumps())

    def getArgs(self):
        shortopt = ['-r', '-b', '-d']
        args = getopt.getopt(sys.argv, shortopts=shortopt)[1]

        if (len(args) < 3):
            print("Need arguments")
            sys.exit()

        args[2] = os.path.abspath(args[2])
        # args[2] = os.path.basename(args[2])
        return args[1:]

    def getcmd(self):
        modes = {
            "-b" : "build",
            "-r" : "run",
            "-d" : "delete"
        }
        self.mode = modes[self.mode]
        self.ext = os.path.splitext(self.file)[1][1:]
        if (self.ext == 'out'):
            return "./$1"
        lang = None
        for k,v in self.doc.items():
            if v.get("extension") == self.ext:
                lang = v
                break
        if (lang == None):
            sys.exit()
            return
        if (not lang.get(self.mode)):
            print(f"Edit the configuration file for {self.mode} mode.")
            sys.exit()
        return lang.get(self.mode)

    def run(self):
        mode = '-r'
        cmd = self.getcmd()
        
        if (len(cmd) == 0):
            print("Command not found")
            sys.exit()
        cmd = sub(r'\$1', self.file, cmd)
        process = subp.run(cmd, shell=True)
        if (process.returncode != 0):
            print(process.stderr)
            sys.exit()
        
    def build(self):
        mode = '-b'
        cmd = self.getcmd()
    
        if (len(cmd) == 0):
            return ""
    
        # $1 -> input file
        # $2 -> output file
        filename = os.path.splitext(self.file)[0]
        cmd = sub(r'\$1', self.file, cmd)
        cmd = sub(r'\$2', filename+'.out', cmd)
        process = subp.run(cmd, shell=True)
        if (process.returncode != 0):
            print(process.stderr)
            return ""
        return filename+".out"
    
    def delete(self):
        process = subp.run(f"rm {self.file}", shell=True)
        if (process.returncode != 0):
            print(process.stderr)
            sys.exit()

if __name__ == "__main__":
    Builder().main()


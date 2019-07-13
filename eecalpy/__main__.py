import sys
import os.path
import eecalpy

usage = '''eecalpy - Electrical Engineering Calculations for Python

Usage:
* eecalpy console                     -- runs the interactive eecalpy shell
* eecalpy script [script_file}        -- run the script file 'script_file' with eecalpy
'''
def main(args=None):
    if args is None:
        args = sys.argv[1:]
    
    if len(args) == 1:
        if args[0] == 'console':
            eecalpy.ee_console()
    elif len(args) == 2:
        if args[0] == 'script' and os.path.isfile(args[1]):
            eecalpy.ee_script_file(args[1])
    else:
        print(usage)

if __name__ == '__main__':
    main()
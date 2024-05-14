# getting the name of the directory
# where the this file is present.
import os
import sys


current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to 
# the sys.path.
sys.path.append(parent)

from raw_scripts.raw_script_v3_function import main_code

i = 1
while i <= 30:
    main_code(f"{i:02}")
    print("Factura "+f"{i:02}"+": ok")
    i=i+1
    
    
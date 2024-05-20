# getting the name of the directory
# where the this file is present.
import os
import sys
import time


current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to 
# the sys.path.
sys.path.append(parent)

from raw_scripts.raw_script_v3_function import main_code

start_time = time.time()

i = 1
while i <= 30:
    try:
        main_code(f"{i:02}")
        print("Factura "+f"{i:02}"+": ok")
        i=i+1
    except:
        print("Factura "+f"{i:02}"+": bad")
        i=i+1

print("Process finished --- %s seconds ---" % (time.time() - start_time))
    
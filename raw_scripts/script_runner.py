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


def write_file(filepath, text):
    # For test
    f = open(filepath, "a")
    f.write(text)
    f.close()
    #######


from lib.enums.image_type_enum import Image_type
from raw_scripts.raw_script_v3_function import main_code

print("Scan Casa Process started")
start_time = time.time()
i = 1
while i <= 30:
    try:
        inner_time = time.time()
        main_code(f"{i:02}", "testing_scan_casa", Image_type.scan)
        write_file("times.txt", "%s\n" % (time.time() - inner_time))
        print("Factura " + f"{i:02}" + " scan: ok")
    except:
        print("Factura " + f"{i:02}" + " scan: bad")
    i = i + 1
print("Scan Casa Process finished --- %s seconds ---" % (time.time() - start_time))

print("Photo Moto Process started")
start_time = time.time()
i = 1
while i <= 30:
    try:
        inner_time = time.time()
        main_code(f"{i:02}", "testing_moto", Image_type.photo)
        write_file("times.txt", "%s\n" % (time.time() - inner_time))
        print("Factura " + f"{i:02}" + " photo: ok")
    except:
        print("Factura " + f"{i:02}" + " photo: bad")
    i = i + 1
print("Photo Moto Process finished --- %s seconds ---" % (time.time() - start_time))

print("PDF Process started")
start_time = time.time()
i = 1
while i <= 30:
    inner_time = time.time()
    try:
        main_code(f"{i:02}", "testing", Image_type.pdf)
        write_file("times.txt", "%s\n" % (time.time() - inner_time))
        print("Factura " + f"{i:02}" + " pdf: ok")
    except:
        print("Factura " + f"{i:02}" + " pdf: bad")
    i = i + 1
print("PDF Process finished --- %s seconds ---" % (time.time() - start_time))

print("Photo Process started")
start_time = time.time()
i = 1
while i <= 30:
    inner_time = time.time()
    try:
        main_code(f"{i:02}", "testing_photo", Image_type.photo)
        write_file("times.txt", "%s\n" % (time.time() - inner_time))
        print("Factura " + f"{i:02}" + " photo: ok")
    except:
        print("Factura " + f"{i:02}" + " photo: bad")
    i = i + 1
print("Photo Process finished --- %s seconds ---" % (time.time() - start_time))

print("Scaned Process started")
start_time = time.time()
i = 1
while i <= 30:
    try:
        inner_time = time.time()
        main_code(f"{i:02}", "testing_scan", Image_type.scan)
        write_file("times.txt", "%s\n" % (time.time() - inner_time))
        print("Factura " + f"{i:02}" + " scan: ok")
    except:
        print("Factura " + f"{i:02}" + " scan: bad")
    i = i + 1
print("Scaned Process finished --- %s seconds ---" % (time.time() - start_time))

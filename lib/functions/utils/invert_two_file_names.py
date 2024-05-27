import os


def invertTwoFileNames(file1Path, file2Path):
    os.rename(file1Path, "images/pretemp/aux.png")
    os.rename(file2Path, file1Path)
    os.rename("images/pretemp/aux.png", file2Path)

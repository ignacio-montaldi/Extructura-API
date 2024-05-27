import os
import shutil

# Borra los archivos temporales


def deleteFilesInFolder(folderPath, fileNamePrefix=None, deleteDirectories=False):
    folder = folderPath
    for filename in os.listdir(folder):
        if fileNamePrefix is None or filename.startswith(fileNamePrefix):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path) and deleteDirectories:
                    shutil.rmtree(file_path)
            except Exception as e:
                print("Failed to delete %s. Reason: %s" % (file_path, e))

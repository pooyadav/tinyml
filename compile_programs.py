"""Compiles the programs for our connected MCU and stores them inside the same
folders used for training that hold the model .pb files as well as the converted
C++ files."""
from subprocess import run
import numpy as np
import time
from pathlib import Path
import shutil
import util


ROOT_MODEL_DIR = Path.cwd() / 'train' / 'models'
ROOT_MBED_PROGRAM_DIR = Path.cwd() / 'mcu_program'


def process_model_folder(model_folder):
    """Process model folders. Checks whether or not there is a .cpp, .hpp, and
    weights file. If there is, then we copy these files to our MBED program,
    and attempt compiling. If we get a successful result, then we copy the
    .bin file corresponding program back into our models file so we can flash
    the MCU with the file later.
    
    @param model_folder: Path object corresponding to the model .pb folder.
    """
    mcu_name = util.get_mcu()
    cpp_files = list(model_folder.glob("*.[h|c]pp"))
    if not cpp_files:
        print(f"There were no c++ files found, skipping directory {model_folder}")
        return

    # If we found C++ files, make sure that there are only 3, and we can copy
    # this to our mbed program, and attempt to compile.
    print("Copying files to our MBED program directory.")
    for cpp_source_file in cpp_files:
        shutil.copy(cpp_source_file, ROOT_MBED_PROGRAM_DIR)
    
    # Now call the compilation.
    run(['sh', 'compile.sh'], cwd=ROOT_MBED_PROGRAM_DIR)
    compiled_binary_files = list((ROOT_MBED_PROGRAM_DIR / 'BUILD').glob("*/*/*.bin"))
    if not compiled_binary_files:
        print("Couldn't find the compiled binary")
        return
    compiled_binary_file = compiled_binary_files[0]

    # If this was successful, copy the file back to our model directory.
    compiled_path = model_folder / '{}_prog.bin'.format(mcu_name)
    shutil.copy(compiled_binary_file, compiled_path)
    

def main():
    root_dir = ROOT_MODEL_DIR
    if not root_dir:
        raise RuntimeError("Model root directory doesn't exist, check path.")

    model_folders = list(root_dir.glob('*'))
    print(f'Found model folders: {model_folders}')
    for model_folder in model_folders:
        process_model_folder(model_folder)


if __name__ == '__main__':
    main()
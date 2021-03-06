import sys
import json
import subprocess
import glob
import os
import re
import argparse
from task import Task
from shutil import copyfile, rmtree
from distutils.dir_util import copy_tree

filepath =  os.path.dirname(os.path.abspath(__file__))
template_path = filepath + "/" + "template.c"

class MnistFC(Task):
    def __init__(self):
        self.parser = argparse.ArgumentParser()

        self.parser.add_argument("--h1_size", default=None, type=int)
        self.parser.add_argument("--h2_size", default=None, type=int)

    def replace_params(self, template, data):
        for k,v in data.items():
            kstr = "{{%s}}" % k
            template = template.replace(kstr, str(v))
        return template

    def generate_task(self, output_path, args):                
        assert(args.h1_size is not None)
        assert(args.h2_size is not None)    
        
        # Copy source files over
        source_files = ["%s/src" % filepath, "%s/train" % filepath]
        for src in source_files:

            src_name = src.split("/")[-1]
            if os.path.isdir(src):
                copy_tree("%s" % src, output_path+"/"+src_name)
            else:
                copyfile(src, output_path + "/" + src_name) 

        # Run the script to generate hpp
        cmd = "bash train_and_generate.sh %d %d" % (args.h1_size, args.h2_size)
        commands = ["cd %s/train && %s" % (output_path, cmd)]
        process = subprocess.Popen(commands, stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()

        print(out.decode('utf-8'))

        # Run another script to evaluate the network on mnist
        # and gather parameters to channel to the cpp script
        cmd = "bash gather_channeled_data.sh %d %d" % (args.h1_size, args.h2_size)
        commands = ["cd %s/train && %s" % (output_path, cmd)]        
        process = subprocess.Popen(commands, stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()
        out = out.decode('utf-8').strip()
        channeled_data = json.loads(out.split("\n")[-1])
        print(channeled_data)

        # Remove the train directory
        rmtree("%s/train" % output_path)

        # Super hacky, but replace the src/main.cpp file with template
        # and insert args + results
        with open("%s/src/main.cpp" % output_path, "r") as f:
            template = f.read()
            template = self.replace_params(template, channeled_data)

        with open("%s/src/main.cpp" % output_path, "w") as f:
            f.write(template)
    
    def task_name(self):
        return "MnistFC"

    def get_parser(self):
        return self.parser
        

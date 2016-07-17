#!/usr/bin/env python
"""
Python wrapper for automatically picking OTUs using NINJA-OPS and generating QIIME outputs from raw sequences
"""

import os
from multiprocessing import cpu_count
import argparse
import sys
import subprocess

def make_arg_parser():
    parser = argparse.ArgumentParser(description='Automated QIIME workflow with NINJA-OPS')
    parser.add_argument('-i', '--inputfile', help='Raw sequences file', required=True)
    parser.add_argument('-o', '--outputdir', help='Output directory', required=True)    
    parser.add_argument('-t', '--ggtreefile', help='Green Genes tree file', required=True)
    parser.add_argument('-s', '--similarity', default=.97, type=float, choices=range(0,1), 
                        help='Similarity threshold for OTU clustering, default: .97')
    return parser


def run_command(cmd):
    try:
        output = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=True,
            cwd=os.getcwd(),
        )

    except subprocess.CalledProcessError as e:
        output = 1
	
    return output

def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

def main():

    try:
        parser = make_arg_parser()
        args = parser.parse_args()

        # this will automatically raise an exception if the directory exists already
        os.makedirs(args.outputdir)

        # check that input file exists
        if not os.path.exists(args.inputfile):
            raise FileNotFoundError(1, 'Cannot find input file', args.inputfile)

        # check that ninja.py is executable accessible
        ninjafile=None
        for path in os.environ['PATH'].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path,'ninja.py')
                if is_exe(exe_file):
                    ninjafile=exe_file
                    break
        if ninjafile==None:
            raise FileNotFoundError(1, 'Cannot locate ninja.py. Have you added its bin folder to PATH?')

        # check that gg db tree is accessible
        if not os.path.exists(args.ggtreefile):
            raise FileNotFoundError(1, 'Cannot locate green genes tree file', args.ggtreefile)

        # format bash script with params here:
        print('Picking OTUs...')
        command_pickotus = '\"%s\" -i \"%s\" -o \"%s\" -s \"%s\" -z' % (ninjafile, args.inputfile, args.outputdir, args.similarity)
        print(command_pickotus)
        if run_command(command_pickotus)==1: # raise an exception here instead 
            raise RuntimeError('Error while picking OTUs')     
    
        #rename otu file
        os.rename(args.outputdir + "/ninja_otutable.biom", args.outputdir + "/otu.biom")

        print('Generating QIIME output...')
        command_generate_output = './make.output.sh \"%s\" \"%s\" \"%s\" 2>&1 | tee -a \"%s\"' % (args.outputdir, args.outputdir+"/otu.biom", args.ggtreefile, args.outputdir+"/qiime.log.txt")
        if run_command(command_generate_output)==1:
            raise RuntimeError('Error while generating QIIME output')

        # print up to 50 lines of biom summary 
        file = open(args.outputdir + "/otu_summary.txt", 'r')
        for i in range(1,50):
            file.readline()

        depth = raw_input('Please enter a rarefaction depth:')
        if not depth.isdigit(): 
            raise TypeError(1, 'Depth is not a number')

        print('Rarefying and generating QIIME output ...')
        command_generate_output_rare = './make.output.sh \"%s\" \"%s\" \"%s\" \"%s\" 2>&1 | tee -a \"%s\"' % (args.outputdir, args.outputdir+"/otu.biom", args.ggtreefile, depth, args.outputdir+"/qiime.log.rare.txt")
        if run_command(command_generate_output_rare)==1:
            raise RuntimeError('Error while generating QIIME output for rarefied OTU table')
            
    except BaseException as e:
        print(str(e))
    
if __name__ == '__main__':
    # Python syntax to run main when script is called
    main()
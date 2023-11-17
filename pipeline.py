#! /usr/bin/env python3

import os
import argparse
import subprocess

import Bio.Blast.Applications
import Bio.SeqIO
import Bio.SeqRecord

# valid fasta endings
FASTA_ENDS = (".fasta",".fa",".fas")
# valid sequence types
FASTA_TYPES = ('nucl', 'prot')

# setting up arguments
parser = argparse.ArgumentParser(description="pipeline script to take query sequence and fastas, and create blast database, blasts the sequences, aligns output, and creates tree")

parser.add_argument("-q", required=True, type=str, help="query sequence")
parser.add_argument("-qtype",required=True, choices=FASTA_TYPES, type=str, help="querry sequence type (prot, nucl)")
parser.add_argument("-fastas", required=True, type=str, help="directory location of fasta file(s)")
parser.add_argument("-ftype", required=True, type=str, choices=FASTA_TYPES, help="database fasta type (prot, nucl)")

parser.add_argument("-threads", type=int, default=1, help="number of threads subprocesses can use")
#parser.add_argument("-mem", type=str, default="1000000", help="memory subprograms are allowed to use")

args = parser.parse_args()

def make_blast_database(fastas: str, type: str) -> None:
    """uses makeblastdb to create blast formatted database from fasta file(s) in input directory

    Args:
        fastas (str): location of fasta file(s)
        type (str): type of fasta file(s) (nucl/prot)
    """

    # run makeblastdb for each file in directory
    for entry in os.scandir(fastas):
        if entry.is_file() and entry.name.endswith(FASTA_ENDS):
                command = f"makeblastdb -in {entry.path} -parse_seqids -dbtype {type}".split(" ")
                subprocess.run(command)

    # make a directory to put output
    bdb = f"{os.getcwd()}/blastdb"
    if not os.path.exists(bdb):
        os.mkdir(bdb)

    # move file outputs to new blastdb directory
    for entry in os.scandir(fastas):
        if entry.is_file():
            if not entry.name.endswith(FASTA_ENDS):
                os.rename(entry.path, f"{bdb}/{entry.name}")
                continue
            subprocess.run(f"cp ./{entry.path} {bdb}/".split(" "))


    
make_blast_database(args.fastas, args.ftype)

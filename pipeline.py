#! /usr/bin/env python3
import os
import argparse
import subprocess
from typing import Union

from Bio.Blast import NCBIXML
from Bio import SearchIO
from Bio import SeqIO

# valid fasta endings
FASTA_ENDS = (".fasta",".fa",".fas")
# valid sequence types
FASTA_TYPES = ('nucl','prot') 

def add_to_name(file: str, addition: str) -> str:
    """adds extension to original filename before last "." in name

    Args:
        file (str): file name, usually DirEntry.name
        addition (str): addition to add

    Returns:
        str: new filename output
    """

    last_dot_index = file.rfind('.')
    outfile = file[:last_dot_index] + addition + file[last_dot_index:]
    return outfile

def remove_extension(file: str) -> str:
    """removes extension after final "."

    Args:
        file (str): name of file

    Returns:
        str: file without everything after and including the last "."
    """
    last_dot_index = file.rfind('.')
    outfile = file[:last_dot_index]
    return outfile


def run_make_blast_database(fastas: str, type: str) -> None:
    """uses makeblastdb to create blast formatted database from fasta file(s) in input directory

    Args:
        fastas (str): location of fasta file(s)
        type (str): type of fasta file(s) (nucl/prot)
    """

    # run makeblastdb for each file in directory
    for entry in os.scandir(fastas):
        if entry.is_file() and entry.name.endswith(FASTA_ENDS):
                makeblastdb_cmd = f"makeblastdb -in {entry.path} -parse_seqids -dbtype {type}".split(" ")
                subprocess.run(makeblastdb_cmd)

    # make a directory to put output
    bdb = f"{os.getcwd()}/blastdb"
    os.makedirs(bdb, exist_ok=True)

    # files to blastdb: copy if fasta, move if blastdb files
    for entry in os.scandir(fastas):
        if entry.is_file():
            if not entry.name.endswith(FASTA_ENDS):
                os.rename(entry.path, f"{bdb}/{entry.name}")
                continue
            copy_fastas_cmd = f"cp ./{entry.path} {bdb}/".split(" ")
            subprocess.run(copy_fastas_cmd)

def run_blast(query: str, qtype: str, ftype: str, threads: int, maxseqs: int) -> None:
    """performs blast using run_make_blast_database output and querry input

    Args:
        query (str): fasta sequence to use as a blast querry
        qtype (str): type of querry sequence (nucl/ prot), used to decide which blast to use
        ftype (str): type of fasta sequences in blast database, used to decide which blast to use
        threads (int): threads the blast subprocess is allowed to use
        maxseqs (int): max target sequences in each blast
    """

    # determine blast type to use (blastn, blastp, blastx, tblastn)
    blast_type= ""

    # python 3.10+ and I don't feel like dealing with environments
    #types = (qtype, ftype)
    #match types:
    #    case ("nucl", "nucl"):
    #        blast_type += "blastn"
    #    case("nucl", "prot"):
    #        blast_type += "blastx"
    #    case("prot", "nucl"):
    #        blast_type += "tblastn"
    #    case("prot", "prot"):
    #        blast_type += "blastp"

    types = (qtype, ftype)
    if types == ("nucl", "nucl"):
        blast_type += "blastn"
    elif types == ("nucl", "prot"):
        blast_type += "blastx"
    elif types == ("prot", "nucl"):
        blast_type += "tblastn"
    elif types == ("prot", "prot"):
        blast_type += "blastp"

    # for every fasta file within the blast database
    bdb = f"{os.getcwd()}/blastdb"
    for entry in os.scandir(bdb):
        if entry.is_file() and entry.name.endswith(FASTA_ENDS):
            print(f"blasting {entry.name}")

            # run and save blast output (XML format) to new file ending with "_blastout"
            blast_cmd = blast_type + f" -query {query} -db {entry.path} -outfmt 5 -max_target_seqs {maxseqs} -evalue 0.00001 -num_threads {threads}"
            result = subprocess.run(blast_cmd.split(" "), stdout=subprocess.PIPE)
            new_outfile = remove_extension(entry.name) + "_blastout"
            with open(new_outfile, 'w') as file:
                file.write(result.stdout.decode("ascii"))
    
    # make a directory to put output
    blastout = f"{os.getcwd()}/blastout"
    os.makedirs(blastout, exist_ok=True)

    # move file to blastout directory
    for entry in os.scandir(os.getcwd()):
        if entry.is_file() and entry.name.endswith("_blastout"):
            os.rename(entry.path, f"{blastout}/{entry.name}")

def find_fastas(ids: Union[list[str], set[str], tuple[str]]) -> None:
    """takes in a collection of sequence headers, and generates a new fasta file with all sequences associated with the headers

    Args:
        ids (Union[list[str], set[str], tuple[str]]): collection of sequence headers
    """

    unused_ids = list(ids)
    used_ids = []
    with open("alignment_seqs.fasta", "w") as fasta_out:
        for entry in os.scandir(args.fastas):
                if not entry.is_file() or not entry.name.endswith(FASTA_ENDS):
                            continue
                for record in SeqIO.parse(entry.path, "fasta"):

                    if record.id in ids:
                        SeqIO.write(record, fasta_out, "fasta")
                        unused_ids.remove(record.id)
                        used_ids.append(record.id)
                    elif record.id in used_ids:
                        print(f"duplicate sequence with header {record.id} ignored")
    if len(unused_ids) > 0:
        for item in used_ids:
            print(f"No sequence found for header {item}")

def create_fasta() -> None:
    """takes the xml outputs of run_blast(), concatinates the sequences into fastas, then concatentates the fastas into one overall fasta for alignment
    """

    # for each blast output xml, get the names of sequences that had hsps (really inefficient probably)
    seq_ids = set()
    blastout = f"{os.getcwd()}/blastout"
    for entry in os.scandir(blastout):
        if entry.is_file() and entry.name.endswith("_blastout"):
            for qresult in SearchIO.read(entry.path, "blast-xml"):
                seq_ids.add(qresult.id)
    find_fastas(seq_ids)
            # with open(entry.path, "r") as xml_handle:
            #     for record in NCBIXML.parse(xml_handle):
            #         for alignment in record.alignments:
            #             for hsp in alignment.hsps:
            #                 print(alignment.title.split(" ")[0])
            #                 print(alignment.length)
            #                 print(hsp.strand)


def run_macse(macse_location: str) -> None:
    """uses output of create_fasta() to create initial alignment of sequences

    Args:
        macse_location (str): location of macse jar file
    """
    
    macse_cmd = f"java -jar {macse_location} -prog alignSequences -seq alignment_seqs.fasta -out_NT alignment_NT_withFS.fasta -out_AA alignment_AA_withFS.fasta"
    subprocess.run(macse_cmd.split(" "))

    # run this first to have stats before macse removes frameshifts and stop codons for use in tree creation
    macse_info_cmd = f"java -jar {macse_location} -prog exportAlignment -align alignment_NT_withFS -out_stat_per_seq alignment_seq_stats.csv -out_stat_per_site alignment_frequencies_stats.csv"
    subprocess.run(macse_info_cmd.split(" "))

    # run this second, reason above
    macse_export_cmd = f"java -jar {macse_location} -prog exportAlignment -align alignment_NT_withFS.fasta -codonForInternalStop NNN -codonForInternalFS - -charForRemainingFS - -out_NT alignment_NT_NoFS.fasta -out_AA alignment_AA_NoFS.fasta -"
    subprocess.run(macse_export_cmd.split(" "))

    # create alignment directory and move all macse files into it
    alignment = f"{os.getcwd()}/alignment"
    os.makedirs(alignment, exist_ok=True)
    for entry in os.scandir(os.getcwd()):
        if entry.is_file() and entry.name.startswith("alignment"):
            os.rename(entry.path, f"{alignment}/{entry.name}")

def run_IQ_tree():
    return

### Running the code ###

# setting up arguments
parser = argparse.ArgumentParser(description="pipeline script to take query sequence and fastas, and create blast database, blasts the sequences, aligns output, and creates tree")

parser.add_argument("-q", required=True, type=str, help="query sequence")
parser.add_argument("-qtype",required=True, choices=FASTA_TYPES, type=str, help="querry sequence type (prot, nucl)")
parser.add_argument("-fastas", required=True, type=str, help="directory location of fasta file(s)")
parser.add_argument("-ftype", required=True, type=str, choices=FASTA_TYPES, help="database fasta type (prot, nucl)")
parser.add_argument("-max_targets", type=int, default=10, help="max number of target seqs while running blast")
parser.add_argument("-a", "-alignemnt", type=str, help="location of macse jar file, if not given, script will stop after blast output")

parser.add_argument("-threads", type=int, default=1, help="number of threads subprocesses can use")
#parser.add_argument("-mem", type=str, default="1000000", help="memory subprograms are allowed to use")

args = parser.parse_args()

#run_make_blast_database(args.fastas, args.ftype)
#run_blast(args.q, args.qtype, args.ftype, args.threads, args.max_targets)
#create_fasta()
if args.a is not None:
    run_macse(args.a)


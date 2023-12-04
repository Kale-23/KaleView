#! /usr/bin/env python3

from typing import List
import pytermgui as ptg
from Bio import Phylo, SearchIO, AlignIO
from prettytable import PrettyTable
import contextlib
import os
import io
import csv
import re

def out_phylo() -> str:
    """reads in phylogenetic tree input and outputs ascii tree

    Returns:
        str: ascii tree representation of phylogenetic tree input
    """
    tree = Phylo.read(f"{os.getcwd()}/tree/alignment_NT_NoFS.fasta.treefile", "newick")
    #who tf wants a function that could return a string to just print straight to stdout???
    # catches the stdout ascii tree and stores as string
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        Phylo.draw_ascii(tree)
    output = f.getvalue()
    return output

def gui_ize(tree: str = out_phylo()) -> ptg.Container:
    """takes in out_phylo() ascii tree and outputs in Container format

    Args:
        tree (str, optional): ascii tree. Defaults to out_phylo().

    Returns:
        ptg.Container: _description_
    """
    # split tree by before/ after tip label (assuming tip label starts with lower/upper alphabet)
    lines = []
    for line in tree.split("\n"):
        pattern = r'(^[^a-zA-Z]+)' 
        lines.append(re.split(pattern, line))

    #TODO potentially fix button and/or make simplier to get rid of regex/ button functionality
    cont = ptg.Container()
    for line in lines:
        if line[-1] != "":
            temp = ptg.Splitter(
                #ptg.Label("".join(line[0:len(line) - 1]), parent_align=0),
                ptg.Label("".join(line), parent_align=0),
                #ptg.Button(line[-1], parent_align=0)
            )
        else:
            temp = ptg.Label("".join(line), parent_align=0)
        cont._add_widget(temp)

    return(cont)

def blast_table(id: str) -> ptg.Label:
    """outputs blast stats in a Label

    Args:
        id (str): valid tip name

    Returns:
        ptg.Label: string table of blast statistics within a Label
    """
    # for each blast output xml, get the names of sequences that had hsps (really inefficient probably)
    seq_ids = set()
    blastout = f"{os.getcwd()}/blastout"
    for entry in os.scandir(blastout):
        if entry.is_file() and entry.name.endswith("_blastout"):
            qresult = SearchIO.read(entry.path, "blast-xml")
            for hit in qresult:
                if hit.id == id:
                    ret = ptg.Label(str(hit))
                    return ret
                    #TODO potentially use other output format that includes more stats
                    # ptg.Container()
                    # print(f"{hit.id}, {hit.seq_len}")
                    # for hsp in hit:
                    #     print(f"{hsp.bitscore}, {hsp.evalue}")
                    #     print(hsp.hit)
                    #     print(hsp.aln_span)
                    #     print(hsp.gap_num)
                    #     print(hsp.ident_num)

                    #     print(hsp.hit.seq)
                    #     print(hsp.aln_annotation["similarity"])
                    #     print(hsp.query.seq)
                # for hsp in hit:
                #     print(hsp)
                # for hit in qresult:
                #     print(hit)
                # seq_ids.add(qresult.id)

#TODO for use in future if alignment view is implemented
#
# def out_alignment(id: str) -> ptg.Container:
#     """outputs macse alignment of tip sequence vs query sequence in a container

#     Args:
#         id (str): valid tip name

#     Returns:
#         ptg.Container: string of macse alignment  within a container
#     """
#     alignment = AlignIO.read(f"{os.getcwd()}/alignment/alignment_NT_NoFS.fasta", "fasta")
#     for record in alignment:
#         if record.id == id:
#             print(record.seq)

def out_alignment_stats(id: str) -> ptg.Container:
    """outputs macse alignment stats for given id

    Args:
        id (str): valid tip name

    Returns:
        ptg.Container: table of alignment stats in a Container
    """
    # grab the correct sequence data
    headers: List[str]
    data: List[str]
    with open(f"{os.getcwd()}/alignment/alignment_seq_stats.csv", "r", newline="") as file_handle:
        reader = csv.reader(file_handle, delimiter=";")
        first = True
        for line in reader:
            if first:
                headers = line
                first = False
            if line[0] == id:
                data = line
        
    # make the table
    tab = PrettyTable()
    tab.field_names = headers
    tab.add_row(data)

    # put table into container and return
    ret = ptg.Container(
        ptg.Label(str(tab))
    )
    return ret

def header_found(id: str) -> bool:
    """checks if tip label input is within the alignment files, use before updating windows

    Args:
        id (str): input tip name

    Returns:
        bool: if tip name was found within alignment files
    """
    with open(f"{os.getcwd()}/alignment/alignment_seq_stats.csv", "r", newline="") as file_handle:
        reader = csv.reader(file_handle, delimiter=";")
        for line in reader:
            if line[0] == id:
                return True
        return False

# def main():
#     """Testing Use"""
#     #out_alignment("E_deani_6_297073")
#     #out_alignment_stats("E_deani_6_297073")
#     print(header_found("E_deani_6_297073"))

# if __name__ == "__main__":
#     main()
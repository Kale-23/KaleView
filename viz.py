#! /usr/bin/env python3

from Bio import Phylo
import os

tree = Phylo.read(f"{os.getcwd()}/tree/alignment_NT_NoFS.fasta.treefile", "newick")
Phylo.draw_ascii(tree)

#! /usr/bin/env python3

from Bio import Phylo
import contextlib
import os
import io
import pytermgui as ptg
import re

def out_phylo() -> str:
    tree = Phylo.read(f"{os.getcwd()}/tree/alignment_NT_NoFS.fasta.treefile", "newick")

    #who tf wants a function that could return a string to just print straight to stdout???
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        Phylo.draw_ascii(tree)
    output = f.getvalue()
    return output

def gui_ize(tree: str = out_phylo()) -> ptg.Container:
    lines = []
    for line in tree.split("\n"):
        pattern = r'(^[^a-zA-Z]+)' 
        lines.append(re.split(pattern, line))

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


def main():
    t = out_phylo()
    gui_ize(t)

if __name__ == "__main__":
    main()
#! /usr/bin/env python3
import pytermgui as ptg



def butt(manager: ptg.WindowManager, window: ptg.Window) -> None:
    for widget in window:
        if isinstance(widget, ptg.Container):
            widget._add_widget(["this is a new widget",], run_get_lines=False)
            continue

    manager.stop()

with ptg.WindowManager() as manager:
    manager.layout.add_slot("Body")
    window = ptg.Window(
        ptg.Container(
            "TREE",
            "STUFF",
            "GOES",
            "HERE"
            "",
            "",
            "",
            "",
            "",
            "-------------------", 
            ["tree tip", lambda*_: butt(manager, window)]
        ),
        ( #splitter
            ptg.Container(
                "BLAST OUTPUT"
            ),
            ptg.Container(
                "SEQUENCE STATS"
            )
        ) #end splitter 
    )

    manager.add(window)
    
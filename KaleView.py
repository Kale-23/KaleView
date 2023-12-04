#! /usr/bin/env python3

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
import time
from typing import Any, Callable, Iterable, Type

import pytermgui as ptg

import viz


class AppWindow(ptg.Window):
    """A generic application window.

    It contains a header with the app's title, as well as some global
    settings.
    """

    app_title: str
    """The display title of the application."""

    app_id: str
    """The short identifier used by ArgumentParser."""

    #standalone: bool
    """Whether this app was launched directly from the CLI."""

    overflow = ptg.Overflow.SCROLL
    vertical_align = ptg.VerticalAlignment.TOP

    def __init__(self, args: Namespace | None = None, **attrs: Any) -> None:
        super().__init__(**attrs)

        #TODO maybe implement this for standalone imput of tip names and direct cmdline output of data
        #self.standalone = bool(getattr(args, self.app_id, None))

        header_box = ptg.boxes.Box(
            [
                "",
                " x ",
                "",
            ]
        )

        self._add_widget(ptg.Container(f"[ptg.title]{self.app_title}", box=header_box))

    def _update(self, *_: Any):
        """updates window contents after a condition is met"""
        return

class Input_Updater(AppWindow):
    """A window for users to input tree tip names"""

    app_title = "Tip Input"
    app_id = "input"

    def __init__(self, args: Namespace | None = None, **attrs: Any) -> None:
        super().__init__(args, **attrs)

        self._input = ptg.InputField("Example_1234", prompt="Tip Name: ")
        self._input.bind(ptg.keys.CARRIAGE_RETURN, lambda*_: updater(self.manager, self._input.value))

        self._content = ptg.Container(self._input)
        self._add_widget(self._content)

    def _update(self, *_: Any) -> None:
        """On update, empties InputField to accept new input"""
        self._content.set_widgets([])

        item = ptg.InputField("", prompt="Tip Name: ")
        item.bind(ptg.keys.CARRIAGE_RETURN, lambda*_: updater(self.manager, item.value))

        self._content.set_widgets(ptg.Container(item))

class TreeWindow(AppWindow):
    """A window to show ascii phylogenetic tree output"""

    app_title = "Tree View"
    app_id = "tree"

    def __init__(self, args: Namespace | None = None, **attrs: Any) -> None:
        super().__init__(args, **attrs)

        self._content = viz.gui_ize()

        self._add_widget(self._content)

class AlignmentView(AppWindow):
    """A window to show alignment statistics of selected tip sequence"""

    app_title = "Alignment Viewer"
    app_id = "alignment"

    def __init__(self, args: Namespace | None = None, **attrs: Any) -> None:
        super().__init__(args, **attrs)

        self._content = ptg.Container(ptg.Label("Input tip name to show alignment stats"))

        self._add_widget(self._content)

    def _update(self, id: str) -> None:
        """updates window to show newly input tip alignment statistics

        Args:
            id (str): tip name
        """
        self._content.set_widgets([])

        item = viz.out_alignment_stats(id)

        self._content.set_widgets(item)

class BlastView(AppWindow):

    app_title = "Blast Viewer"
    app_id = "blast"

    def __init__(self, args: Namespace | None = None, **attrs: Any) -> None:
        super().__init__(args, **attrs)

        self._content = ptg.Container(ptg.Label("Input tip name to show blast stats"))

        self._add_widget(self._content)

    def _update(self, value: str) -> None:
        """updates window to show newly input tip blast statistics

        Args:
            value (str): tip name
        """
        self._content.set_widgets([])

        item = viz.blast_table(value)

        self._content.set_widgets(item)

#TODO use this to do standalone windows
# def _process_arguments(argv: list[str] | None = None) -> Namespace:
#     """Processes command line arguments.

#     Note that you don't _have to_ use the bultin argparse module for this; it
#     is just what the module uses.

#     Args:
#         argv: A list of command line arguments, not including the binary path
#             (sys.argv[0]).
#     """

#     parser = ArgumentParser(description="KaleViewer")

#     return parser.parse_args(argv)

def _create_aliases() -> None:
    """Creates all the TIM aliases used by the application.

    Aliases should generally follow the following format:

        namespace.item

    For example, the title color of an app named "myapp" could be something like:

        myapp.title
    """

    ptg.tim.alias("ptg.title", "secondary bold")
    ptg.tim.alias("ptg.alert", "red bold")


def _configure_widgets() -> None:
    """Defines all the global widget configurations.

    Some example lines you could use here:

        ptg.boxes.DOUBLE.set_chars_of(ptg.Window)
        ptg.Splitter.set_char("separator", " ")
        ptg.Button.styles.label = "myapp.button.label"
        ptg.Container.styles.border__corner = "myapp.border"
    """
    ptg.Splitter.set_char("separator", "")
    ptg.boxes.SINGLE.set_chars_of(ptg.Window)


def _define_layout() -> ptg.Layout:
    """Defines the application layout.

    Layouts work based on "slots" within them. Each slot can be given dimensions for
    both width and height. Integer values are interpreted to mean a static width, float
    values will be used to "scale" the relevant terminal dimension, and giving nothing
    will allow PTG to calculate the corrent dimension.
    """
    layout = ptg.Layout()

    layout.add_slot("Header", height=0.1)
    layout.add_break()

    layout.add_slot("Body", height=0.6)
    layout.add_break()

    layout.add_slot("LowRight", height=0.25, width=0.5)
    layout.add_slot("lowLeft", height=0.25, width=0.5)
    layout.add_break()

    layout.add_slot("Footer", height=0.05)

    return layout

def tip_not_found(man: ptg.WindowManager) -> None:
    """Opens a modal dialogue to warn user that input value was not found"""

    modal = man.alert( "[ptg.alert]Seqence Not Found!", "", center=True)

    time.sleep(2)

    man.remove(modal)

def updater(manager: ptg.WindowManager, value: str) -> None:
    """used to check input and update all windows on valid input

    Args:
        manager (ptg.WindowManager): current window manager
        value (str): user input tip name
    """

    # checks if input value is in alignment
    if not viz.header_found(value):
        tip_not_found(manager)
        return
    
    # updates all windows
    for item in manager:
        if isinstance(item, AppWindow):
            item._update(value)


def main(argv: list[str] | None = None) -> None:
    """Runs the application."""

    _create_aliases()
    _configure_widgets()

    #args = _process_arguments(argv)

    with ptg.WindowManager() as manager:
        manager.layout = _define_layout()

        # Since header is the first defined slot, this will assign to the correct place
        manager.add(Input_Updater())

        footer = ptg.Window(ptg.Button("<O-Q>: Quit", lambda *_: manager.stop()), box="EMPTY")

        # Since the second slot, body was not assigned to, we need to manually assign
        # to "footer"
        manager.add(footer, assign="footer")
        manager.add(TreeWindow(), assign="body")
        manager.add(AlignmentView(), assign="lowright")
        manager.add(BlastView(), assign="lowleft")

        manager.bind(
            "\u0153", # option Q
            lambda *_: (manager.stop()),
            "Close window",
        )

    ptg.tim.print("[!gradient(210)]Goodbye!")

if __name__ == "__main__":
    main(sys.argv[1:])

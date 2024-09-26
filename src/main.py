#!/bin/python3

import logging
import xml.etree.ElementTree as ET

from lint import Lint
from datetime import datetime
from lint.data import Brief, Summary

import tkinter as tk
from tkinter import Tk, Text
from tkinter.ttk import Scrollbar

# TODO This is a temporary function and should be replaced as soon as possible
def dummy_brief_to_text(brief: Brief, summaries: tuple[Summary,...]) -> str:
    summary = summaries[0]

    # TODO: Problem: Item has no title.
    # TODO: Move this to the Brief class

    return (
f"""================================================================================
                                {brief.classification[0]}
================================================================================
                LLM-Based Intelligence Analysis (LINT) Brief Regarding
                                Climate Change


This brief consists of {len(summaries)} summaries.


Information cut off: {brief.cutoff_date}

Language model used for categorisation: Dummy
Language model used for brief writing: Dummy

---------------------------------------------------------------------------------
--      START OF LINT SUMMARY. {datetime.now()}                                --
---------------------------------------------------------------------------------

1. ({summary.classification}) {summary.title}
Information cut off: {brief.cutoff_date}
Source(s): {" ".join([f"[{index+1}]({summary.source_items[index].link})" for index in range(0,len(summary.source_items))])}

{summary.summary}

---------------------------------------------------------------------------------
--       END OF LINT SUMMARY. {datetime.now()}                                 --
---------------------------------------------------------------------------------

This LLM-generated brief does not replace human analysis. Neither guarantee nor
liability is assumed for the correctness and completeness of the information.

================================================================================
                                {brief.classification[0]}
================================================================================""")

def display_text_gui(text: str):
    root = Tk()
    root.resizable(True, True)
    root.title("LINT Prototype Version")
    root.geometry('800x800+100+100')

    xscrollbar = Scrollbar(root, orient=tk.HORIZONTAL)
    xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    yscrollbar = Scrollbar(root, orient=tk.VERTICAL)
    yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    txt_area = Text(root, wrap=tk.NONE, height=80, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
    txt_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    xscrollbar.config(command=txt_area.xview)
    yscrollbar.config(command=txt_area.yview)

    txt_area.insert('1.0', text, ("n",))    # Insert with wrapping-disabled tag
    txt_area['state'] = 'disabled'

    root.mainloop()

def load_opml():
    pass

def main():
    logger = logging.getLogger(__name__)
    try:
        # TODO: Create a loading stage, where configuration and sources are loaded (subroutines)
        lint = Lint.from_xml(ET.parse('config.xml').getroot())
        lint.fetch_items()
        brief, summaries = lint.generate_brief(cutoff_date=datetime.now())
        text = dummy_brief_to_text(brief, summaries)
        # Output text on command line
        print(text)
        # Show in window (currently unused)
        # display_text_gui(text)
    except BaseException as err:
        logger.critical('Program will abort due to critical error:', exc_info=True)
        # This basic print message is just to ensure that the user will get the message,
        # as a redundancy
        print('Aborting program...')

# Only execute the main function if this file is run as a script
if __name__ == "__main__":
    main()

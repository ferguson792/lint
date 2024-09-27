#!/bin/python3

import sys
import traceback
import logging
import xml.etree.ElementTree as ET

from lint import Lint
from datetime import datetime
from lint.data import Brief, Summary
import lint.opml as opml

import tkinter as tk
from tkinter import Tk, Text
from tkinter.ttk import Scrollbar

def print_err(obj):
    print(obj, file=sys.stderr)

BRIEF_TEMPLATE="""
================================================================================
                                {classification}
================================================================================
                LLM-Based Intelligence Analysis (LINT) Brief Regarding
                                Climate Change


This brief consists of {num_summaries} summaries.


Information cut off: {cutoff_date}

Language model used for categorisation: TODO
Language model used for brief writing: TODO

--------------------------------------------------------------------------------
--      START OF LINT SUMMARY. {datetime}                     --
--------------------------------------------------------------------------------
{summaries}
--------------------------------------------------------------------------------
--        END OF LINT SUMMARY. {datetime}                     --
--------------------------------------------------------------------------------

This LLM-generated brief does not replace human analysis. Neither guarantee nor
liability is assumed for the correctness and completeness of the information.

================================================================================
                                {classification}
================================================================================
"""

SUMMARY_TEMPLATE="""
1. ({classification}) {title}
Information cut off: {cutoff_date}
Source Item(s): {items}

{summary}
"""

# TODO This is a temporary ""function and should be replaced as soon as possible
def dummy_brief_to_text(brief: Brief, summaries: tuple[Summary,...]) -> str:
    
    # TODO: Problem: Item has no title (for sources).

    return BRIEF_TEMPLATE.format(
        classification="//".join(brief.classification),
        num_summaries=len(summaries),
        datetime=datetime.now(),
        cutoff_date=brief.cutoff_date,
        summaries="".join([SUMMARY_TEMPLATE.format(
            classification=summary.classification,
            title=summary.title,
            cutoff_date=brief.cutoff_date,
            items=" ".join([f"[{item.uid}]" for item in summary.source_items]),
            summary=summary.summary
            ) for summary in summaries]),
        )

    return output

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

CONFIG_FILENAME = 'config.xml'
SOURCES_FILENAME = 'sources.opml'

def main():
    logger = logging.getLogger(__name__)
    try:
        # TODO: Create a loading stage, where configuration and sources are loaded (subroutines)
        
        # Load configuration
        config_tree = None
        try:
            config_tree = ET.parse(CONFIG_FILENAME)
        except FileNotFoundError as e:
            sys.exit(f"Missing configuration file: {CONFIG_FILENAME}")
        
        # Create LINT from configuration
        lint = Lint.from_xml(config_tree.getroot())       

        # Load sources
        try:
            # TODO Use a function set_sources(), which compares them with the stored sources!
            lint.sources = opml.sources_from_opml(SOURCES_FILENAME)
        except FileNotFoundError as e:
            sys.exit(f"Missing sources file: {SOURCES_FILENAME}")

        lint.fetch_items()
        brief, summaries = lint.generate_brief(cutoff_date=datetime.now())
        text = dummy_brief_to_text(brief, summaries)
        # Output text on command line
        print(text)
        # Show in window (currently unused)
        # display_text_gui(text)


    except Exception as e:
        print_err('Program will abort due to critical error:')
        print_err(traceback.format_exc())
        # This basic print message is just to ensure that the user will get the message,
        # as a redundancy
        sys.exit('Aborted due to critical error')

# Only execute the main function if this file is run as a script
if __name__ == "__main__":
    main()

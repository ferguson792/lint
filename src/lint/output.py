from lint.data import Brief, Summary
import lint.version as version
from datetime import datetime

import tkinter as tk
from tkinter import Tk, Text
from tkinter.ttk import Scrollbar

TEMPLATE_COLUMN_WIDTH=80
BRIEF_TEMPLATE="""
================================================================================
{classification}
================================================================================
             LLM-Based Intelligence Analysis (LINT) Brief Regarding
{topics}


This brief consists of {num_summaries} summaries.


Information cut off: {cutoff_date}

{config_notice}

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

SPACE = ' '
def center_text(column_width: int, text: str) -> str:
    if len(text) > column_width:
        return text
    else:
        diff = column_width - len(text)
        half_diff = diff // 2

        # Difference is either: Even (symmetric), Odd (asymmetric / left-aligned)
        return "".join((
            SPACE * (half_diff if diff % 2 == 0 else half_diff-1),
            text,
            SPACE * half_diff
            ))

# TODO This is a temporary ""function and should be replaced as soon as possible
def brief_to_text(brief: Brief, summaries: tuple[Summary,...]) -> str:
    return BRIEF_TEMPLATE.format(
        classification=center_text(TEMPLATE_COLUMN_WIDTH, "//".join(brief.classification)),
        topics=center_text(TEMPLATE_COLUMN_WIDTH, brief.topic_descriptions),
        num_summaries=len(summaries),
        config_notice=brief.config_notice,
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

_VERSION_MESSAGE=f"""LLM-based Intelligence Analysis (LINT) {version.LINT_VERSION} 
Copyright (C) 2024 LINT Contributors
License AGPLv3+: GNU AGPL version 3 or later <http://gnu.org/licenses/agpl.html>
This is free software; you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law."""

def get_version_message():
    return _VERSION_MESSAGE

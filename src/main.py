#!/bin/python3

import os
import sys
import traceback
import logging
import xml.etree.ElementTree as ET

from lint import Lint
from datetime import datetime
import lint.opml as opml
import lint.output as output
import lint.version as version

import argparse

def _print_err(obj):
    """
    Internal helper function used to print to stderr.
    """
    print(obj, file=sys.stderr)

CONFIG_FILENAME = 'config.xml'
SOURCES_FILENAME = 'sources.opml'

def _setup_parser():
    parser = argparse.ArgumentParser(
        prog="lint",
        description="LLM-based Intelligence Analysis (LINT)")

    # Optional positional argument: Working directory
    parser.add_argument('working_directory', type=str, nargs='?',
                        help="The working directory to be used by LINT")
    
    # Switch: version
    parser.add_argument('--version',
                    action='store_true')  # on/off flag


    return parser

def _run_lint():
    logger = logging.getLogger(__name__)

    try:
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
            # TODO Use a function set_sources() in Lint, which compares them with the stored sources!
            lint.sources = opml.sources_from_opml(SOURCES_FILENAME)
        except FileNotFoundError as e:
            sys.exit(f"Missing sources file: {SOURCES_FILENAME}")

        lint.fetch_items()
        brief, summaries = lint.generate_brief(cutoff_date=datetime.now())
        text = output.brief_to_text(brief, summaries)
        # Output text on command line
        print(text)
        # Show in window (currently unused)
        # output.display_text_gui(text)

    except Exception as e:
        _print_err('Program will abort due to critical error:')
        _print_err(traceback.format_exc())
        # This basic print message is just to ensure that the user will get the message,
        # as a redundancy
        sys.exit('Aborted due to critical error')

def main():
    # First, parse the command line arguments
    parser = _setup_parser()

    args = parser.parse_args()
    # First: Check if there is a version flag
    if args.version:
        print(output.get_version_message())
    else:
        # Check if the working directory should be changed
        if args.working_directory != '?':
            target_directory = args.working_directory
            try:
                os.chdir(target_directory)
            except FileNotFoundError:
                parser.error(f"Directory not found: {target_directory}")
            except NotADirectoryError:
                parser.error(f"Not a directory: {target_directory}")
            except PermissionError:
                parser.error(f"Insufficient permissions to access: {target_directory}")

        # Run LINT
        _run_lint()

# Only execute the main function if this file is run as a script
if __name__ == "__main__":
    main()

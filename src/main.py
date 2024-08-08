#!/bin/python3

from lint import Lint

def main():
    try:
        # Here be code
        lint = Lint()
        lint.fetch_items()
    except BaseException as e:
        # TODO Handle exceptions
        raise e

# Only execute the main function if this file is run as a script
if __name__ == "__main__":
    main()

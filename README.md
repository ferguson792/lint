# LINT
> Version `0.2.0-bleeding.0`
>
> **WARNING:** This is a prototype. Proceed with caution and at your own risk.

For detailed documentation, see [`docs/README.md`](docs/README.md).

LINT has been developed on and optimized for Linux systems.

## How LINT works
TODO

## Running LINT

### Requirements
To run LINT, you need to have the following components installed on your system:

* Python 3.11 or higher
    * [Python Libraries](#python-libraries); see below ↓
* [Make](https://en.wikipedia.org/wiki/Make_(software))

### Python Libraries
> For more information about libraries, view [`docs/dependencies.md`](docs/dependencies.md).

Before running LINT, make sure you have the required libraries installed.

LINT installs these libraries in a local Python virtual environment for testing purposes;
however, if you wish to run them outside of this environment, you need to install the libraries
on your system, e.g. via `pip`.

The build system can install these dependencies automatically in a local Python virtual environemnt (`venv`), and will attempt to do
so if you run LINT through the build system.

To install dependencies automatically for local testing, execute
```sh
$ make local-venv
```

To purge the local venv (e.g. for a clean re-installation), execute
```sh
$ make purge-venv
```

> **NOTE:** Reinstalling all the required libraries is a relatively costly operation in terms of time and bandwith required, so purging the local venv should be a last resort. If the local venv is misconfigured, try fixing the problem manually or, if it persists, consider filing a bug report.

If you want to query Mistral's online API, you will need to generate and store an API key and install the necessary client library as well.
See <https://github.com/mistralai/client-python> for more information.

### Running the program
To run LINT, simply execute
```sh
$ make run [working directory]
```
An optional working directory can be specified, otherwise the current working directory is used.

### Running sample configurations
This repository includes two example configurations in the `sample` sub-directory: "detailed", which includes
a demonstration using Mistral's online API (but requires API keys to be inserted first) and "dummy", which
uses dummy versions of all processing stages.

To run them in this repository, execute
```
$ make run-sample-detailed
```
or
```
$ make run-sample-dummy
```
respectively.

## Packaging LINT
To create a TAR archive, execute
```
$ make dist
```

The archive can be found under `build/dist/lint-<version>.tar.gz`.

## Configuration
LINT is divided into multiple processing stages; each can be configured individually.
See `docs/configuration.md` for more details.

## Sample output
```txt
================================================================================
                                PUBLIC
================================================================================
                LLM-Based Intelligence Analysis (LINT) Brief Regarding
                                Climate Change


This brief consists of 1 summaries.


Information cut off: 2024-08-14 14:13:26.367801

Language model used for categorisation: Dummy
Language model used for brief writing: Dummy

---------------------------------------------------------------------------------
--      START OF LINT SUMMARY. 2024-08-14 14:13:26.415958                      --
---------------------------------------------------------------------------------

1. (PUBLIC) Famous More Despair Rarely Two Reservoir Down They 400-year Water Witness World's X-rays Government Complex UK Oxygen Europe's Satellite Musk's Who
Information cut off: 2024-08-14 14:13:26.367801
Source(s): [1](https://www.bbc.com/news/articles/c207lqdn755o) [2](https://www.bbc.com/news/articles/cy4ldkpz1klo) [+ 19 sources...]

Stonehenge's Campaigners Local A The Studies The Two The Thames Rory A The The Scientists The The After A The A

---------------------------------------------------------------------------------
--       END OF LINT SUMMARY. 2024-08-14 14:13:26.415977                       --
---------------------------------------------------------------------------------

This LLM-generated brief does not replace human analysis. Neither guarantee nor
liability is assumed for the correctness and completeness of the information.

================================================================================
                                PUBLIC
================================================================================
```

## Copyright Notice

LINT ("LLM-based Intelligence Analysis") is a secure, robust and open AI tool for automatically summarising open internet sources.

Copyright (C) 2024  ferguson792, dickey154

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the [GNU Affero General Public License](LICENSE.txt)
along with this program.  If not, see <https://www.gnu.org/licenses/>.

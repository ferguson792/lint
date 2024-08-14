# LINT
> Version 0.1.0-bleeding0
> **WARNING:** This is a prototype. Proceed with caution and at your own risk.

For detailed documentation, see [`docs/README.md`](docs/README.md).

At the moment, dummy processors are used to speed up development and enable rapid prototyping.
Nevertheless, the program already draws in and processes current information, meaning the summaries change
with the progress of time and new information drawn from the single testing source (a BBC newsfeed
about "Science and Environment"). The date for information-cutoff is always the current moment
(Python `datetime.now()`). The viewback timespan is always a period of 48 hours, from the current moment
(i.e. the last two days are being summarized).

## Running LINT

### Requirements
To run LINT, you need to have the following components installed on your system:

* Python 3.11 or higher
    * [Python Libraries](#python libraries); see below ↓
* [Make](https://en.wikipedia.org/wiki/Make_(software))

### Python Libraries
> For more information about libraries, view [`docs/libraries.md`](docs/libraries.md).

Before running LINT, make sure you have the required libraries installed.
To install them via `pip`, run
```sh
$ pip install result requests feedparser
```

### Running the program
To run LINT, simply execute
```sh
$ make run
```

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

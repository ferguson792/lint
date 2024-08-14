# Technical Debt and Potential Pitfalls

This file records _technical debt_: Shortcuts taken during development and routines
which need to be implemented more robustly and/or efficiently (past issues).

It also records _potential pitfalls_: Problems which might arise during development
and cause trouble down the road, if not addressed (future issues).

## Harmonization
> **Note on Terminology:** We do not use the term "synchronization", because that implies mediating
> between different states in time. However, we do not mediate between different states in time,
> but between different states in general. We cannot rely on temporal information alone, because
> temporal information might be corrupted, not accurate and/or reliable enough, or even not available at all.
> We also do not use the term "merging", because merging is just one available route to harmonization.
>
> We use the term "harmonization", because we are dealing with (resolving) conflicts between different states.

Harmonization happens at two levels (in two stages):
First, the sources from an OPML file are compared with the sources stored in the database.
Second, the sources are queried for their items, and compared with the items stored in the database.

The end goal of harmonization is that the state in the program reflects exactly the state in the database.

During both stages, differencs (conflicts) can emerge, and those differences need to be recognized (caught) and
handled appropriately. For sources at least, it is also important and interesting (noteworthy) to keep a record
of conflicts that emerged and how they were resolved. This is important, because it provides a history to the
data, which helps with diagnosing problems more easily, recognizing patterns, and even detecting malicious
activity.

> **Note:** These harmonization issues must be distinguished from the general case of sources being
> unreachable, or the device having no network connection at all. These problems fall into the class of
> "restricted network access" issues and must be handled differently, with one exception:
> Individual sources being unreachable but not others, which might indicate a problem with the source
> instead of the connection.
> **TL;DR:** The operator must distinguish between network issues and isses with and of the source.
> LINT must aid the operator in detecting and distinguishing between these issues.

### Harmonization of Sources

Sources are given in an OPML file, meaning they have a tree-like structure. We can ignore this structure;
the human operator can arbitrarily shuffle sources around. The OPML file should not be given to the core
program directly, since it contains a lot of superficial information for the core routines, and has in all
likelihood already been parsed by the interface. Instead, the core should receive only the information
necessary for performing its work. This is mainly the sources name and link (URI).

The OPML file should also store the internal database ID.

Harmonization is deterministic and all-or-nothing routine, meaning that if conflicts emerge, they are recorded
and returned to the caller, to be handled by the interface. A solution to these conflicts can then be supplied
by the caller in a new call.

> What is the output of source harmonization? A new tuple of sources, with the correct ID assigned to them.
> The order should remain the same, with deleted sources indicated by `None`, and new sources added at the end.
>
> **Subroutine description:**
> Input: An immutable list (tuple) of sources with all necessary attributes filled in.
> Output: A new tuple of sources, reflecting the sources stored in the database, or a tuple of unresolved conflicts.

#### Potential conflicts
> This list is non-exhaustive.

- Source URL same, but other details have changed
- Source from database missing in given sources, but also not marked expired/deprecated
- Source marked deprecated in database, but is not deprecated in list of given sources
- Source without ID (i.e. new source) has been given, but ource with same or similar details is in database

#### Troubleshooting (Conflict + Resolution) History
Whenever a conflict is resolved between given and stored sources, the conflict and its resolution should
be stored in the database.

### Conflict Resolution
_TODO_ How should this work? There should also be a review mechanism in the end, kind of like
with a bank transfer.

## RSS specificity
At the moment, we rely too much on specific details of RSS.

### Retrieval
1. Outsource retrieval into its own submodule.
2. Create a new class for source item retrievers, and then decide depending on the source which individual
retriever to use for each source.

### Raw item extraction
One solution could be to process the entries in parallel: Once with a feedparser, and once with an XML
analyzer. That way we can get both the required attributes and the raw text, since the correct order
of items is guaranteed in both.

## Timekeeping
We use different formats for date and time. We really shouldn't.

One idea could be to unify all data types into a common type, and then create subtypes for each specific type
(reflect the different structures in code).

## Prompt Engineering and Language Model Reliability
Language models are stochastic. Even if the prompt precisely specifies certain output requirements and formats,
it can never be guaranteed that these will be met by the language model. For this reason, potential errors must
be handled appropriately.

Like all unexptected issues and errors, a human must decide how to handle them.
An obvious remedy would be calling the same routine again, with tweaked parameters (_which?_).
However, the remedy should be specified by a human operator, because the very occurrence of such an error is
significant, since it might highlight problems with the text, the source, the prompt or may even be sign of
malicious activity (e.g. LM injections).

> We must be careful not to create "reverse centaurs", where humans must catch the rarest and hardest-to-spot
> errors. Computers are good at vigilance; humans aren't.

## Retrival Problem Resolution (Network and Parser issues)
_TODO_ How should we deal with them?

## Settings

Settings must be split into two parts: Interface settings and core settings.
Core settings are non-persistent, meaning they must be supplied by the interface each time.
Interface settings for the command line interface are also non-persistent.

The command line interface takes these settings via command line arguments.
The graphical interface will probably store them somewhere, since that is the expected behavior.

## Interfaces

Both interfaces should be derived from a common base type, to unify functionality common to both interfaces
(e.g. conflict resolution / harmonization strategies).

## Logging

Logging must be integrated via a centralized system, which should also offer logging levels.
Logging is not automatically written to a file; that must be activated by redirecting output.

# LINT Documentation
Relase: X

## About This Documentation
This documentation is version 1.1 of the LINT documentation.
It is based on the docx version 1 created on 2024-07-09.

This document is the basis for a shared understanding of the software we develop. It supports us in the development process. It defines terms and describes the interaction between different parts of the program.
Changes to the project must be made both in this document and within in the source code. When making changes to the basic architecture described here, it is important to check whether they are compatible with the project outline. If necessary, changes must be coordinated.

## What is LINT?
LINT is a secure, robust and open AI tool for automatically summarising open internet sources. It allows analysts to retrieve and semantically filter a variety of news feeds. The user describes in natural language the topics on which they would like to be informed. News is retrieved from specified sources via [RSS](https://en.wikipedia.org/wiki/RSS) and automatically categorized. LINT uses an offline LLM to provide a daily summary of the current situation, whereby the source is always specified.

## Getting Started
### System Requirements
_To Be Included_

### Installation
_To Be Included_

### Running
_To Be Included_

## Understanding LINT
### Flowchart
_To Be Included_

### Glossary
#### Definition of Key Terms
| Name Konzept Deutsch | Name Concept English | Definition and Explanation Concept (English)  | Datatype Concept | Python Name | Python Data Type | DB Name | DB Datatype |
|----------------------|----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------|-------------|------------------|---------|-------------|
| Quelle               | Source               | A **source** is a web feed that is integrated via RSS. The source is the entire RSS file.                                                                                                                                                                                       | text             | Source |  str |         |             |
| Quellobjekt          | Item                 | An **item** is an entry (item) of a **source**; in other words, an **item** corresponds to the individual message in an RSS feed. An **item** contains all metadata.                                                                                                      | text             | Item | str     |         |             |
| Nachricht            | Message | A **message** is the (semnatic) content transmitted by the **item**; in other words, a **message** corresponds to the individual news item in an RSS feed, which is usually written in natural language. The **message** is made up of `<title>` and `<description>` elements. | text             |             |                  |         |             |
| Klassifikation       | Classification | A **classification** is a vector assigned to a sources which describes how seriously information needs to be protected. The vector has linearly independent bases; some are even flags.                                                                                         | Array            |             |                  |         |             |
| Themenvektor         |  Topic Vector | The **topic vector** is the vector created with the Sentence Transformer, which represents the message content.  | Vector           |             |                  |         |             |
|                      |                      |                                                                                                                                                                                                                                                                             |                  |             |                  |         |             |
|                      |                      |                                                                                                                                                                                                                                                                             |                  |             |                  |         |             |
|                      |                      |                                                                                                                                                                                                                                                                             |                  |             |                  |         |             |
|                      |                      |                                                                                                                                                                                                                                                                             |                  |             |                  |         |             |
|                      |                      |                                                                                                                                                                                                                                                                             |                  |             |                  |         |             |
|                      |                      |                                                                                                                                                                                                                                                                             |                  |             |                  |         |             |

### Descritption of Key Components
#### Source Database (Quellen-Datenbank)
| Name Konzept Deutsch | Name Concept English | Definition and Explanation Concept (English) | Datatype Concept | Python Name | Python Data Type | DB Name | DB Datatype |
|----------------------|----------------------|----------------------------------------------|------------------|-------------|------------------|---------|-------------|
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |

#### Item Database (Quellobjekt-Datenbank)
| Name Konzept Deutsch              | Name Concept English | Definition and Explanation Concept (English)                                                                                                                                                                | Datatype Concept | Python Name | Python Data Type | DB Name | DB Datatype |
|-----------------------------------|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------|-------------|------------------|---------|-------------|
| Quellobjekt-Datenbank-Eintrags-ID |  Item ID  | Automatically generated ID                                                                                                                                                                                  | number           |             |                  |         |             |
| Quellobjekt                       |  Item | The unprocessed **item**.                                                                                                                                                                                | text             |             |                  |         |             |
| Abrufdatum                        |  Retrieval Date | The time at which LINT retrieved the QUELLE.                                                                                                                                                                | datetime         |             |                  |         |             |
| Quellenname                       |   Source Name  | The name of the **source** as defined by the user in the OPML file.                                                                                                                                             | text             |             |                  |         |             |
| Quellen-Link                      |   Source Link   | The hyperlink to the feed of the **source**.                                                                                                                                                                    | text             |             |                  |         |             |
| Klassifikation                    |  Classification | **Classification** of the **item**                                                                                                                                                                     | Array            |             |                  |         |             |
| Quarantäne-Provenienz             |  Quarantine Indicator | Note on whether the **item** was in quarantine and the relevant circumstances, as well as a note on the processing steps used to remove the entry from quarantine.                                       | ?                | QuarantineIndicator  |                  |         |             |
| 

Verarbeitungsvermerk     |   Processing Status | Note on how the **item** was processed. (0: Default when creating the item "not processed". 1: In processing for _Message Database_. 2: Fully pre-processed in _Message Database_). | number           |             |                  |         |             |
|                                   |                      |                                                                                                                                                                                                             |                  |             |                  |         |             |
|                                   |                      |                                                                                                                                                                                                             |                  |             |                  |         |             |              |             |                  |         |             |              |             |                  |         |             |              |             |                  |         |             |              |             |                  |         |             |

#### Message Batabase (Temporäre-Nachrichten-Datenbank)
| Name Konzept Deutsch | Name Concept English | Definition and Explanation Concept (English) | Datatype Concept | Python Name | Python Data Type | DB Name | DB Datatype |
|----------------------|----------------------|----------------------------------------------|------------------|-------------|------------------|---------|-------------|
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |

#### Brief Database (Bericht-Datenbank)
| Name Konzept Deutsch | Name Concept English | Definition and Explanation Concept (English) | Datatype Concept | Python Name | Python Data Type | DB Name | DB Datatype |
|----------------------|----------------------|----------------------------------------------|------------------|-------------|------------------|---------|-------------|
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |
|                      |                      |                                              |                  |             |                  |         |             |

## License
To Be Included

## Technical Debt / Open Issues
Currently in technical_debt.md, in the future in the GitHub Issues.

## Contact
If you have any questions, please contact us via GitHub.

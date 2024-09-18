from result import Ok, Err, Result, is_ok, is_err
import feedparser
from datetime import datetime

import requests

from lint.data import Source, SourceType, Item, ProcessingStatus
from lint.processors import QuarantineIndicator

# Constants required for the item-detection algorithm
ITEM_OPENING = "<item>"
ITEM_CLOSING = "</item>"

def get_items_raw(text: str) -> Result[list[str], ValueError]:
        """
        This is a bespoke algorithm which gets all the items enclosed with
        <item>...</item> tags from the given text.
        The desired output is achieved by counting braces.
        The rules are:
            1. A closing </item> must come after an opening <item>
            2. An opening <item> must come after a closing </item>
            3. The first tag must be an <item>
            4. No nested <item> tags
        """
        items: list[str] = []
        pos_opening = 0
        pos_closing = 0
        while pos_opening > -1 and pos_closing > -1:
            # Find the next opening <item>
            pos_opening = text.find(ITEM_OPENING, pos_opening+1)

            # If the next opening position is behind the previous opening position, return an error
            if pos_opening != -1 and pos_opening < pos_closing:
                print(text[pos_opening:pos_closing+len(ITEM_CLOSING)])
                return Err(ValueError(f"Next opening position {pos_opening} is behind previous closing position {pos_closing}"))

            # Find the next closing </item>
            pos_closing = text.find(ITEM_CLOSING, pos_closing+1)

            # Check if either is -1 (Not Found), but not the other. Return an error in that case
            if pos_closing == -1 and pos_opening != -1:
                return Err(ValueError(f"No closing position found, but opening position is {pos_opening}"))
            if pos_closing != -1 and pos_opening == -1:
                return Err(ValueError(f"No opening position found, but closing position is {pos_closing}"))
            
            # If the next closing position is behind the next opening position, return an error
            if pos_closing < pos_opening:
                # If the opening position is not smaller than the closing position,
                # we have detected an error
                return Err(ValueError(f"Opening position {pos_opening} after closing position {pos_closing}"))
            
            if pos_closing != -1 and pos_opening != -1:
                # Append the substring corresponding to the new entry
                items.append(text[pos_opening:(pos_closing+len(ITEM_CLOSING))])
        
        return Ok(items)

def fetch_source_items(source: Source, quarantine_indicator: QuarantineIndicator) -> Result[list[Item], ValueError]:
    if source.type == SourceType.RSS or source.type == SourceType.ATOM:
        return fetch_rss_atom(source, quarantine_indicator)
    else:
        return Err(ValueError(f"Unknown source type: {source.type}"))

def fetch_rss_atom(source: Source, quarantine_indicator: QuarantineIndicator) -> Result[list[Item], ValueError]:
    if not (source.type == SourceType.RSS or source.type == SourceType.ATOM):
        return Err(ValueError(f"Attempting to parse source of type {source.type} as Atom/RSS"))

    # Load feed file from source
    access_date = datetime.now()
    response_text = requests.get(source.uri).text

    # First: Get item XML (raw)
    items_raw_result = get_items_raw(response_text)
    if is_err(items_raw_result):
        return Err(items_raw_result.err_value)
    
    # Extract raw items XML from Result
    items_raw = items_raw_result.ok_value

    # Second: Parse RSS/Atom feed with feedparser
    feed = feedparser.parse(response_text)

    # Sanity check: Does the feed match the source type?
    if feed.version == "":
        return Err(ValueError("Fetched source feed has unknown format (feedparser version)"))
    if not ((source.type == SourceType.RSS and feed.version.startswith('rss')) or (source.type == SourceType.ATOM and feed.version.startswith('atom'))):
        return Err(ValueError(f"Source feed does not match type: Type {source.type} and Feed Version '{feed.version}'"))
    
    # Check whether the feed has exactly as many elements as the XML result
    if len(items_raw) != len(feed.entries):
        return Err(ValueError(f"Number of raw items does not match number of feed items: {len(items_raw)} != {len(feed.entries)}"))

    # Parse items
    items = []
    for i in range(0, len(items_raw)):
        item_raw = items_raw[i]
        item_feed = feed.entries[i]

        # TODO Use bozo flag of feedparser to tag items as coming from a Bozo source (or tag the source as bozo?)
        # TODO If the link is none and guid is none we have a Uniqueness problem. Should we resort to the description or title?
        #   -> This should be handled by the caller. This routine simply returns the parse results
        link = item_feed.link
        guid = item_feed.id
        pub_date = item_feed.published

        # TODO Classification is taken straight from the source. In the future, there should be a standard for that,
        #  maybe an additional classifier
        items.append(
            Item(uid=None, link=link, guid=guid, pub_date=pub_date, raw_item=item_raw,
            source=source, access_date=access_date, classification=source.classification,
            quarantine_status=quarantine_indicator.indicate_for_text(item_raw), processing_status=ProcessingStatus.UN_PROCESSED)
        )
    
    return Ok(items)

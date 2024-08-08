from lint.data import Source, SourceType, SourceStatus, Item, ProcessingStatus
from lint.processors import QuarantineIndicator, NeverMaliciousDetector
from lint.storage import StorageManager
from result import Ok, Err, Result, is_ok, is_err

import re
import requests
import xml.etree.ElementTree as ElementTree
from datetime import datetime

# Constants required for the item-detection algorithm
ITEM_OPENING = "<item>"
ITEM_CLOSING = "</item>"

XMLNS_REGEX = re.compile('xmlns:[A-Za-z0-9]+?=".*?"')

class RssSourceRetriever:
    def get_items_xml(text: str) -> Result[list[str], ValueError]:
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


    def fetch_items(self, sources: tuple[Source,...], quarantine_indicator: QuarantineIndicator) -> list[Item]:
        items = []

        for source in sources:
            # Load RSS file from source
            response = requests.get(source.uri)
            access_date = datetime.now()

            item_with_xmlns = "<item {}>".format(" ".join(XMLNS_REGEX.findall(response.text)))

            # Parse as XML
            items_xml_result = RssSourceRetriever.get_items_xml(response.text)

            # Ignore problems
            # TODO We can't just ignore all problems. There should be a problem resolution mechanism.
            if is_ok(items_xml_result):
                # Parse individual XML elements
                items_xml = items_xml_result.ok_value
                for item_xml in items_xml:
                    try:
                        # TODO This is a dirty hack to avoid the problems with missing namespaces
                        #   and no long-term solution:
                        # Simply append the missing namespaces to the item itself, by replacing it
                        item_xml_parsed = ElementTree.fromstring(item_xml.replace("<item>", item_with_xmlns, 1))
                    except ElementTree.ParseError as e:
                        print(item_xml)
                        raise e
                    
                    # We find only the first occurence of a tag.
                    # TODO Duplicate tags might indicate bozo RSS and should be at least flagged
                    # TODO If the link is none and guid is none we have a Uniqueness problem. Should we resort to the description or title?
                    link = item_xml_parsed.find("link").text
                    guid = item_xml_parsed.find("guid").text
                    pub_date = item_xml_parsed.find("pubDate").text
                    # TODO Classification is taken straight from the source. In the future, there should be a standard for that.
                    items.append(
                        Item(uid=None, link=link, guid=guid, pub_date=pub_date, raw_item=item_xml,
                        source_uid=source.uid, access_date=access_date, classification=source.classification,
                        quarantine_status=quarantine_indicator.indicate_for_text(item_xml), processing_status=ProcessingStatus.UN_PROCESSED)
                    )
            else:
                print(f"Error while processing source {source}: {items_xml_result.err_value}")
        
        return items


class Lint:
    sources: tuple[Source,...] = (
        Source(None, "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml", ("PUBLIC",), SourceType.RSS, SourceStatus.LIVE),)
    items = []

    sm: StorageManager = StorageManager("test.db")
    retriever = RssSourceRetriever()
    qi = QuarantineIndicator(NeverMaliciousDetector(), NeverMaliciousDetector())

    def fetch_items(self):
        # Zeroeth step: Update sources
        sources_update_result = self.sm.update_sources(self.sources)
        if is_ok(sources_update_result):
            self.sources = sources_update_result.ok_value

            # First step: Retrieve items from sources
            retrieved_items = self.retriever.fetch_items(self.sources, self.qi)
            print(retrieved_items)

            # Next step: Store (synchronize) those items in the database
            items_sync_result = self.sm.synchronize_items(retrieved_items)
            if is_ok(items_sync_result):
                self.items = items_sync_result.ok_value
                print()
                print(self.items)
        else:
            raise sources_update_result.err_value


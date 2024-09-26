from result import Ok, Err, Result, is_ok, is_err
from datetime import datetime
import time
import logging
from typing import Self

import feedparser

from lint.configuration import *

from lint.data import Source, SourceType, SourceStatus, Item, ProcessingStatus, Message, Brief, Summary
from lint.processors import *
from lint.storage import StorageManager
import lint.subroutines.retrieval as retrieval

def datetime_to_posix_timestamp(date_time: datetime) -> int:
    return int(time.mktime(date_time.timetuple()))

_LOG_FORMAT = '[%(asctime)s %(levelname)s:%(name)s] %(message)s'
_DEBUG_OUTPUT_DEFAULT_VALUE: bool = False

class Lint(XmlConfigurable):
    logger = logging.getLogger(__name__)

    sources: tuple[Source,...] = []
    items: list[Item] = []

    # TODO Wouldn't it be better if the StorageManager controlled the items?
    store: StorageManager = StorageManager("test.db")
    
    qi: QuarantineIndicator
    briefing_parameters: BriefingParameters
    categorizer: MessageCategorizer
    estimator: RelevanceEstimator
    summarizer: MessageSummarizer

    def __init__(self,
                 quarantine_indicator: QuarantineIndicator,
                 briefing_parameters: BriefingParameters,
                 estimator: RelevanceEstimator,
                 categorizer: MessageCategorizer,
                 summarizer: MessageSummarizer,
                 debug_output: bool=_DEBUG_OUTPUT_DEFAULT_VALUE):
        # Set the logging level based on the configuration
        # (This has to be the first instruction, because a  lot of logging will happen during the configuration...)
        logging.basicConfig(encoding='utf-8', level=(logging.DEBUG if debug_output else logging.INFO), format=_LOG_FORMAT)

        # Set the processor objects
        self.qi = quarantine_indicator
        self.estimator = estimator
        self.categorizer = categorizer
        self.summarizer = summarizer

        # Briefing
        self.briefing_parameters = briefing_parameters
    
    @classmethod
    def get_xml_tag(cls) -> str:
        return "lint"

    @classmethod
    def from_xml(cls, root: ET.Element) -> Self:
        """
        Loading a configuration works by interpreting the tree recursively.
        Each sub-configuration is responsible for interpreting its own part of the tree.
        """
        Lint.logger.debug("Applying configuration...")

        # Check whether the root tag is correct
        if root.tag != "lint":
            raise ConfigurationError(f"Root tag is not <lint>: {root.tag}")
        
        # Check whether debug output is configured
        debug_output = _DEBUG_OUTPUT_DEFAULT_VALUE
        try:
            debug_output = text_to_bool(find_single(root, "debug-output", must_exist=False).text)
        except ValueError as err:
            raise ConfigurationError(f"Unknown value for <debug-output>: {err}", err)
        
        # Root node for briefing configuration
        briefing_node = find_single(root, "briefing")

        def instantiate_processor(node: ET.Element, surrounding_node: str, available_types: list):
            return instantiate_type_from_xml(find_single(find_single(node, surrounding_node), "processor"), available_types)

        lint = Lint(
            quarantine_indicator = QuarantineIndicator.from_xml(find_single(root, "quarantine")),
            briefing_parameters = BriefingParameters.from_xml(find_single(briefing_node, "parameters")),
            estimator = instantiate_processor(briefing_node, "relevance", RelevanceEstimator.available_types),
            categorizer = instantiate_processor(briefing_node, "categorization", MessageCategorizer.available_types),
            summarizer = instantiate_processor(briefing_node, "summary", MessageSummarizer.available_types),
            debug_output = debug_output
        )

        Lint.logger.debug("Configuration has been applied.")

        return lint

    def fetch_items(self):
        # Zeroeth step: Update sources
        # TODO: Insert a harmonizer between the storage manager and the LINT object
        sources_update_result = self.store.update_sources(self.sources)
        if is_ok(sources_update_result):
            self.sources = sources_update_result.ok_value

            # First step: Retrieve items from sources
            retrieved_items = []
            for source in self.sources:
                retrieved_items.extend(retrieval.fetch_source_items(source, self.qi).ok_value)
            # print(retrieved_items)

            # Next step: Store (synchronize) those items in the database
            items_sync_result = self.store.synchronize_items(retrieved_items)
            if is_ok(items_sync_result):
                self.items = items_sync_result.ok_value
                # print()
                # print(self.items)
        else:
            raise sources_update_result.err_value

    def _preprocess_items(self, cutoff_date: datetime, viewback_ms: int, ignore_pub_date: bool, ignore_processing_status: bool) -> list[Message]:
        """
        Preprocesses those items which have been marked as UN_PROCESSED, and afterwards
        sets their status to PRE_PROCESSED. If ignore_processing_status is set, the processing status
        is ignored.
        """
        # TODO We should honor the publication date, although that may be more difficult...
        # TODO In the future, we should query the database directly, so not all messages have to be held in memory
        
        time_threshold = datetime_to_posix_timestamp(cutoff_date) - viewback_ms
        
        # This checks whether an item should be (pre-)processed
        predicate = (
            (lambda item: datetime_to_posix_timestamp(item.access_date) > time_threshold)
            if ignore_processing_status
            else (lambda item: datetime_to_posix_timestamp(item.access_date) > time_threshold and item.processing_status == ProcessingStatus.UN_PROCESSED))
        
        def preprocess_item(item):
            # Update item processing status
            if item.processing_status == ProcessingStatus.UN_PROCESSED:
                item.processing_status = ProcessingStatus.PRE_PROCESSED
            # Extract title and description via feedparser (TODO: This is another dirty hack that needs to go soon)
            feed = feedparser.parse(f"<rss><channel>{item.raw_item}</channel></rss>")
            # TODO We need to improve this routine and handle missing elements
            entry = feed.entries[0]
            return Message(
                uid=None, item=item,
                title=entry.title, description=entry.description, relevance=None, relevance_context=None, topic_vector=None, cluster=None)
        
        # Loop over items and select those which fit our criteria
        # Convert selected items into messages
        # For all items selected, update their processing status to PRE_PROCESSED, if it is UN_PROCESSED
        # TODO Store in database
        # TODO Create a processor to convert an item into a message, to get both title and description!
        return [
            preprocess_item(item)
            for item in self.items if predicate(item)]

    def generate_brief(self, cutoff_date: datetime, viewback_ms: int, relevance_threshold: int=50, ignore_pub_date: bool=False, ignore_processing_status: bool=False) -> tuple[Brief, tuple[Summary, ...]]:
        # TODO Clear temporary database table for messages
        # Preprocess items and store in temporary message database
        messages = self._preprocess_items(cutoff_date, viewback_ms, ignore_pub_date, ignore_processing_status)
        # Estimate relevance (with context) and topic vector
        for message in messages:
            relevance, relevance_context = self.estimator.estimate_relevance(message)
            message.relevance = relevance
            message.relevance_context = relevance_context
            # TODO Remove this dummy statement
            message.cluster = 0
        # TODO Update result in storage
        # TODO Cluster, based on topic vector (with relevance)
        # TODO Update result in storage
        # TODO It might be beneficial to adjust relevance for each cluster?
        # Create a Brief object
        brief = Brief(uid=None, cutoff_date=cutoff_date, viewback_ms=viewback_ms, classification=("PUBLIC",), prompt_relevance="", prompt_summary="")
        # Create summaries for each cluster
        title, summary_text = self.summarizer.summarize(messages)
        summary = Summary(
            uid=None, brief=brief, generation_date=(time.time_ns() // 1_000_000),
            title=title, summary=summary_text, cluster=0, classification="PUBLIC",
            source_items=self.items, issued=False)

        # TODO Create and store brief in database

        return (brief, (summary,))

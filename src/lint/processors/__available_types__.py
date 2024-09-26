from lint.processors.interface import *

# Register available types in the relevant class objects
# by overriding the relevant class variable
import lint.processors.dummy as dummy
import lint.processors.detectors as detectors
import lint.processors.lmbased as lmbased

MaliciousDetector.available_types = [dummy.DummyMaliciousDetector, detectors.BlackListDetector]
RelevanceEstimator.available_types = [dummy.DummyRelevanceEstimator, lmbased.LmBasedRelevanceEstimator]
MessageCategorizer.available_types = [dummy.DummyMessageCategorizer]
MessageSummarizer.available_types = [dummy.DummyMessageSummarizer, lmbased.LmBasedMessageSummarizer]

import xml.etree.ElementTree as ET

from lint.data import Source, SourceType, SourceStatus, ClassificationLevels

DEFAULT_CLASSIFICATION: ClassificationLevels = tuple()

def sources_from_opml(path: str) -> list[Source]:
    sources = []
    
    tree = ET.parse(path)
    for node in tree.findall('.//outline'):
        source_type = node.attrib.get('type')
        if source_type:
            if source_type == 'rss':
                url = node.attrib.get('xmlUrl')
                if url:
                    # TODO Currently, only a single classification can be used...
                    classification = node.attrib.get('classification')
                
                    sources.append(Source(
                        # These are default values for sources loaded from an OPML
                        uid=None,
                        status=SourceStatus.UNKNOWN,

                        # If no classification exists, the default value is used (an empty tuple)
                        classification=(classification,) if classification else DEFAULT_CLASSIFICATION,
                        
                        # Load from source
                        uri=url,
                        type=SourceType.RSS
                    ))
                else:
                    raise ValueError(f"Outline is of type 'rss' but has no 'xmlUrl' attribute: {node}")
            else:
                raise ValueError(f'Cannot process sources of type: {source_type}')
    
    return sources

import logging
from typing import Self
import xml.etree.ElementTree as ET

from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.cluster import MeanShift
import matplotlib.pyplot as plt
import numpy as np

from lint.processors.interface import MessageCategorizer
from lint.data import Message
from lint.configuration import get_attrib_or_err, find_single

class SentenceTransformerCategorizer(MessageCategorizer):
    logger = logging.getLogger(__name__)

    def __init__(self, model_name: str):
        self.model_name = model_name
        # Load a pretrained Sentence Transformer model
        self.model = SentenceTransformer(model_name)

    def cluster(self, messages: list[Message]) -> list[tuple[Message, ...]]:
        self.logger.debug(f"Received {len(messages)} messages for clustering")

        # Calculate embeddings (aka tensor representation of the sentence) by calling model.encode()
        embeddings = self.model.encode([message.text() for message in messages])

        # Just for debugging:
        #np.set_printoptions(threshold=np.inf)
        #print(embeddings)

        # Just for debugging
        #np.savetxt('embeddings.txt', embeddings)

        # Dimension of embeddings
        embedding_dimensionality = embeddings.shape[1]

        # Calculates minimum needed for dimension reduction using PCA
        embeddings_samples, embeddings_features = embeddings.shape
        embeddings_components = min(embeddings_samples, embeddings_features)

        self.logger.debug(f"Shape embedding: {embedding_dimensionality}")

        # Reduce dimensionality to 2D for visualization
        pca_visual = PCA(n_components=2)
        #pca_calculation = PCA(n_components=embeddings_components)
        #set to 2 because of better performance
        pca_calculation = PCA(n_components=2)
        reduced_tensor_visual = pca_visual.fit_transform(embeddings)
        reduced_tensor_calculation = pca_calculation.fit_transform(embeddings)

        # Fit MeanShift to the embeddings
        mean_shift = MeanShift()
        #TODO For some reason, mean_shift only works for the tensors reduced in dimension.
        #   (Should also work on higher dimension, which is preferable as reducing dimensions reduces nuances in the classification.)
        mean_shift.fit(reduced_tensor_calculation)

        # Get the cluster labels
        labels = mean_shift.labels_

        self.logger.debug(f"Labels ({type(labels)}): length = {len(labels)}")

        # Empty dictionary for the cluster labels
        labeled_clusters = { }
        num_clusters = 0

        # Create the clusters based on the labels
        for i, message in enumerate(messages):
            # TODO Also assign the topic vector from the embeddings
            cluster_label = labels[i]
            # Assign the cluster label to the message
            message.cluster = cluster_label

            # If this is the first message with that label (i.e. cluster),
            # create a new empty list
            if cluster_label not in labeled_clusters:
                labeled_clusters[cluster_label] = []
                # Increment the number of clusters
                num_clusters += 1
            
            # Add the message to that cluster
            labeled_clusters[cluster_label].append(message)
        
        self.logger.debug(f"Categorized into {num_clusters} clusters with lengths {[len(labeled_clusters[i]) for i in range(num_clusters)]}")

        return [tuple(labeled_clusters[i]) for i in range(num_clusters)]

    #override
    def get_config_notice(self) -> str:
        return f"{super().get_config_notice()}:{self.model_name}"

    #override
    @classmethod
    def get_type(cls) -> str:
        return "sentence-transformer"
    
    #override
    @classmethod
    def from_xml(cls, node: ET.Element) -> Self:
        # Model name can be configured via XML
        return SentenceTransformerCategorizer(get_attrib_or_err(find_single(node, "model"), "type"))

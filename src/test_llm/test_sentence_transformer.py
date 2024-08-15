# source test_llm.env/bin/activate
# To Instll Sentence Transfomer see: https://www.sbert.net/docs/installation.html
# install scikit-learn and numpy
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.cluster import MeanShift
import matplotlib.pyplot as plt
import numpy as np

# Load a pretrained Sentence Transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# The sentences / messages to encode (examples)
sentences = [
    "The weather is lovely today.",  # 0
    "It's so sunny outside!",         # 1
    "What a beautiful day it is!",    # 2
    "He drove to the stadium.",        # 3
    "She enjoys painting landscapes.",  # 4
    "They are planning a trip to the mountains.",  # 5
    "I love reading mystery novels.",  # 6
    "She enjoys thrillers and suspense stories.",  # 7
    "He can't get enough of detective fiction.",  # 8
    "The cat is sleeping on the couch.",  # 9
    "He plays the guitar beautifully.",  # 10
    "They are cooking dinner together.",  # 11
    "The flowers are blooming in spring.",  # 12
    "Trees are starting to bud.",  # 13
    "Birds are singing in the morning.",  # 14
    "She is learning to play the piano.",  # 15
    "He runs every morning for exercise.",  # 16
    "They are watching a movie tonight.",  # 17
    "I enjoy hiking in the mountains.",  # 18
    "She loves exploring nature trails.",  # 19
    "They often go camping in the woods.",  # 20
    "The dog barked at the mailman.",  # 21
    "He is studying for his exams.",  # 22
    "I hate this"  # 23
]



# Calculate embeddings (aka tensor representation of the sentence) by calling model.encode()
embeddings = model.encode(sentences)

# Reduce dimensionality to 2D for visualization
pca = PCA(n_components=2)
reduced_tensor = pca.fit_transform(embeddings)

# Fit MeanShift to the embeddings
mean_shift = MeanShift()
#TODO For some reason, mean_shift only works for the tensors reduced in dimension. Should also work on higher dimension, which is preferable as reducing dimensions reducies nounaces in the clasifiation.
mean_shift.fit(reduced_tensor)

# Get the cluster labels
labels = mean_shift.labels_

print(labels)

# Create a color map based on the unique labels
unique_labels = np.unique(labels)
colors = plt.cm.get_cmap('viridis', len(unique_labels))  # You can choose other colormaps

# Plot the reduced tensor with colors based on labels
plt.figure(figsize=(10, 8))
for i, label in enumerate(unique_labels):
    # Get the indices of the points belonging to the current label
    label_indices = np.where(labels == label)
    plt.scatter(reduced_tensor[label_indices, 0], reduced_tensor[label_indices, 1],
                color=colors(i), label=f'Cluster {label}', alpha=0.7)

# Annotate each point with its corresponding index
for i in range(reduced_tensor.shape[0]):
    plt.annotate(i, (reduced_tensor[i, 0], reduced_tensor[i, 1]), fontsize=8, alpha=0.5)

plt.title('PCA of High-Dimensional Tensor with MeanShift Clustering')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.legend()
plt.show()

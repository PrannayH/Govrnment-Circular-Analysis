import spacy
from spacy.training import Example
from spacy.util import compounding, minibatch
import json
from tqdm import tqdm
import random

# Load the blank model
nlp = spacy.blank("en")

# Function to load data from train.txt
def load_data(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    data = eval(content)  # This assumes the data is in a Python list format in the file
    return data

# Path to the train.txt file
file_path = "train.txt"

# Load the data
TRAIN_DATA = load_data(file_path)

# Create the annotations in the required format
train_data = []
for entry in TRAIN_DATA:
    text = entry[0]
    entities = [(start, end, label) for start, end, label in entry[1]['entities']]
    train_data.append((text, {"entities": entities}))

# Create the NER pipeline component and add it to the pipeline
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner")

# Add the labels to the NER component
for _, annotations in train_data:
    for ent in annotations.get("entities"):
        ner.add_label(ent[2])

# Start the training
optimizer = nlp.begin_training()

# Hyperparameters
n_iter = 125
dropout_rate = 0.05
learn_rate = compounding(1e-4, 1e-2, 1.001)
batch_sizes = compounding(4.0, 32.0, 1.001)

# Training the NER model
for itn in range(n_iter):
    print(f"Iteration {itn}")
    losses = {}
    random.shuffle(train_data)  # Shuffle the training data
    batches = minibatch(train_data, size=batch_sizes)
    for batch in tqdm(batches):
        texts, annotations = zip(*batch)
        examples = [Example.from_dict(nlp.make_doc(text), ann) for text, ann in zip(texts, annotations)]
        nlp.update(examples, drop=dropout_rate, sgd=optimizer, losses=losses)
    print(f"Losses at iteration {itn}: {losses}")

# Save the trained model
output_dir = "output_model125"
nlp.to_disk(output_dir)
print(f"Saved model to {output_dir}")

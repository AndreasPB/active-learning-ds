#!/usr/bin/env python3
import numpy as np
from tf_keras.layers import Dense, Flatten
from tf_keras.layers import Embedding
from tf_keras.models import Sequential
from tf_keras.models import load_model
from tf_keras.optimizers.legacy import SGD
from tf_keras.preprocessing.sequence import pad_sequences
from tf_keras.preprocessing.text import Tokenizer

np.set_printoptions(suppress=True)

# Depends on the selection of the pre-trained embedding dictionary
EMBEDDING_VECTOR_LENGTH = 100

# The percentage of dataset to use for validation (the rest is for training)
VALIDATION_SPLIT = 0.1

# How sure (in percentage) the network has to be to consider a classification of an individual sample successful
SUCCESS_THRESHOLD = 0.9

# The overall classification success threshold
TRAINING_SUCCESS_THRESHOLD = 0.95
TRAINING_MAX_EPOCHS = 200

# --- Load dataset ---
messages = []  # list of text samples
labels = []  # 1 spam; 0 ham
with open("../datasets/spam-dataset.csv", newline="") as dataset_file:
    i = 0
    for row in dataset_file:
        row_split = row.split(",", 1)
        if "spam" == row_split[0]:
            labels.append(1)
        elif "ham" == row_split[0]:
            labels.append(0)
        else:
            # Skip if it's an unknown category
            continue

        messages.append(row_split[1])
print(f"Found {len(messages)} texts.")

# Make them numpy arrays and shuffle
perm = np.random.permutation(len(messages))
messages = np.array(messages)[perm]
labels = np.array(labels)[perm]

# Tokenize words and convert messages into sequences
tokenizer = Tokenizer()
tokenizer.fit_on_texts(messages)
sequences = tokenizer.texts_to_sequences(messages)
word_index = tokenizer.word_index
print(f"Found and tokenized {len(word_index)} unique words.")

# Use pre-trained GloVe embeddings (vector length is 100): https://github.com/stanfordnlp/GloVe
embeddings_dict = {}
print("Loading pre-trained embeddings...")
with open("../datasets/glove.6B.100d.txt") as f:
    for line in f:
        word, coeffs = line.split(maxsplit=1)
        coeffs = np.fromstring(coeffs, "f", sep=" ")
        embeddings_dict[word] = coeffs
print(f"Found {len(embeddings_dict)} word vectors.")

# Prepare embedding matrix
word_number = len(word_index) + 1  # +1 because 0 is reserved for misses
hits = 0
misses = 0
embedding_matrix = np.zeros((word_number, EMBEDDING_VECTOR_LENGTH))
for word, index in word_index.items():
    embedding_vector = embeddings_dict.get(word)
    if embedding_vector is not None:
        # Words not found in embedding index (and index 0 of course) will be a vector of all zeros.
        embedding_matrix[index] = embedding_vector
        hits += 1
    else:
        misses += 1
print(f"Converted {hits} words ({misses}).")

np.save("tokenizer_word_index.npy", tokenizer.word_index)
np.save("embedding_matrix.npy", embedding_matrix)
print("Tokenizer and embedding_matrix saved!")

# Split dataset on validation and training
validation_texts_number = int(VALIDATION_SPLIT * len(sequences))
train_sequences = sequences[:-validation_texts_number]
validation_sequences = sequences[-validation_texts_number:]
train_labels = labels[:-validation_texts_number]
validation_labels = labels[-validation_texts_number:]

# Padding sequences by the longest one (adds 0s for smaller sequences)
longest_sequence = 0
for sequence in sequences:
    longest_sequence = (
        longest_sequence if len(sequence) <= longest_sequence else len(sequence)
    )
print(f"Longest sequence is {longest_sequence}.")
padded_train_sequences = pad_sequences(
    train_sequences, maxlen=longest_sequence, padding="post"
)
padded_validation_sequences = pad_sequences(
    validation_sequences, maxlen=longest_sequence, padding="post"
)

# --- Build the prediction model ---
model = Sequential()
model.add(
    Embedding(
        input_dim=word_number,
        output_dim=EMBEDDING_VECTOR_LENGTH,
        weights=[embedding_matrix],
        input_length=longest_sequence,
        trainable=False,
    )
)
model.add(Flatten())
model.add(Dense(128, activation="sigmoid"))
model.add(Dense(1, activation="sigmoid"))
model.compile(optimizer=SGD(learning_rate=0.01), loss="mean_squared_error")
model.summary()

# --- Train the model ---


epoch_count = 1
print("Training started...")

# TODO: Der må være en pænere måde at gøre det her på
while True:
    model.fit(padded_train_sequences, train_labels)
    classifications = model.predict(padded_validation_sequences)

    # I can do this better with evaluations, but ok for now
    success_count = 0
    for i in range(len(classifications)):
        if classifications[i] > SUCCESS_THRESHOLD and validation_labels[i] == 1:
            success_count += 1
        elif classifications[i] < 1 - SUCCESS_THRESHOLD and validation_labels[i] == 0:
            success_count += 1
    success_rate = success_count / len(padded_validation_sequences)
    print("----------------------------------------")
    print(f"[End of epoch {epoch_count}]")
    print(f"Success rate: {success_rate}")
    print("----------------------------------------")
    if success_rate >= TRAINING_SUCCESS_THRESHOLD or epoch_count == TRAINING_MAX_EPOCHS:
        break
    epoch_count += 1


# --- Save the model ---
model.save("spam_detection_model.h5")
print("Model saved!")


# Print false classifications
classifications = model.predict(padded_validation_sequences)
print("---------------------------------------")
print("[False classifications in the validation sample (sequences)]")
for i in range(len(classifications)):
    if (
        (classifications[i] > SUCCESS_THRESHOLD and validation_labels[i] == 0)
        or (classifications[i] < 1 - SUCCESS_THRESHOLD and validation_labels[i] == 1)
        or (SUCCESS_THRESHOLD > classifications[i] > 1 - SUCCESS_THRESHOLD)
    ):
        print(
            "- "
            + str(tokenizer.sequences_to_texts(validation_sequences)[i])
            + ": "
            + str(classifications[i])
        )
print("---------------------------------------")

# Classify a couple of samples that are not in the dataset
print("---------------------------------------")
print("[Manual examples]")
samples = [
    "Do you mind booking this hotel for our trip? Last cheap room here: https://somewebsite.com/foo",
    "Cheap booking, last chance: https://somewebsite.com/foo. Act now before it's too late",
]

# --- Test the saved models ---

# Load the saved model and tokenizer
loaded_model = load_model("spam_detection_model.h5")
loaded_tokenizer = Tokenizer()
loaded_tokenizer.word_index = np.load(
    "tokenizer_word_index.npy", allow_pickle=True
).item()

# Test the loaded model
sample_sequences = loaded_tokenizer.texts_to_sequences(["Test sample"])
padded_sample_sequences = pad_sequences(
    sample_sequences, maxlen=longest_sequence, padding="post"
)
sample_classifications = loaded_model.predict(padded_sample_sequences)
print("Loaded model classification:", sample_classifications[0])
for i in range(len(sample_classifications)):
    print("- " + str(samples[i]) + ": " + str(sample_classifications[i]))

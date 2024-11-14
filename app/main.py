from fastapi.responses import RedirectResponse

from fastapi import FastAPI
from tensorflow.keras.saving import load_model
import numpy as np
from tf_keras.preprocessing.sequence import pad_sequences
from tf_keras.preprocessing.text import Tokenizer

try:
    # Load the saved model and tokenizer
    loaded_model = load_model("models/spam_detection_model.h5")
    tokenizer = Tokenizer()
    tokenizer.word_index = np.load(
        "models/tokenizer_word_index.npy", allow_pickle=True
    ).item()
except Exception as e:
    print("This probably means that you need to train the model")
    print("Error:", e)


app = FastAPI()


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


@app.post("/predict")
async def predict(text: str):
    # Tokenize the input text
    sequence = tokenizer.texts_to_sequences([text])[0]

    # Pad the sequence to match the model's input length
    # TODO: better way of setting the longest_sequence up
    # longest_sequence if len(sequence) <= longest_sequence else len(sequence)
    # the hardcoded 23 is from looking at logs during training
    padded_sequence = pad_sequences(
        [sequence],
        maxlen=(23 if len(sequence) <= 23 else len(sequence)),
        padding="post",
    )

    prediction = loaded_model.predict(padded_sequence)

    # Convert prediction to binary classification (spam or not spam)
    predicted_class = np.round(prediction[0]).astype(int)[0]

    # Create response
    if predicted_class == 1:
        result = f"The text '{text}' is classified as SPAM."
    else:
        result = f"The text '{text}' is classified as HAM."

    print("\n\nprediction:", prediction)
    return {"prediction": result, "confidence": float(round(prediction[0][0], 2))}


@app.post("/train")
async def train(type: str, header: str, context: str, handling: str):
    # TODO: Tokenize inputs and send to a model for the type of match
    return {"result": "The model has been improved and is now better than ever! 🦄"}


@app.get("/experiment")
async def experiment():
    print("experiment")

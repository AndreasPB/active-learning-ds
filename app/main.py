from fastapi.responses import RedirectResponse
from fastapi import FastAPI
from .models.nn import Net

app = FastAPI()


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/predict")
def predict(header: str, context: str):
    # TODO: Get prediction from a model
    return {"result": "50% sure there's something here 🤷"}


@app.post("/train")
def train(header: str, context: str, handling: str):
    # TODO: Tokenize inputs and send to a model
    return {"result": "The moel has been improved and is now better than ever! 🦄"}


@app.get("/experiment")
def experiment():
    net = Net()
    print(net)
    return net

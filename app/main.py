from fastapi.responses import RedirectResponse
from fastapi import FastAPI

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
    # TODO: Send inputs to a model
    return {"result": "The model has been improved and is better than ever! 🦄"}

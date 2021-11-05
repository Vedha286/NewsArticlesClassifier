import uvicorn
from pydantic import BaseModel
from modelTrainingService.traning import train, load_model
from modelPredictionService.modelPrediction import predict
from starlette import requests
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Form

templates = Jinja2Templates(directory="views")
app = FastAPI(title="News Classifier", docs_url="/docs")
#app.add_event_handler("startup", load_model)

class NewsClassifierRetrainStatusOut(BaseModel):
    Status: str
    Accuracy: str
    Classifier: str

class NewsClassifierQueryIn(BaseModel):
  News: str

class NewsClassifierQueryOut(BaseModel):
    Category: str

@app.get("/ping")
# Healthcheck route to ensure that the API is up and running
def ping():
    return {"ping": "pong"}

@app.get("/")
def load_Home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/retrain_news_category")
def retrain_news_category(request: Request):
      classifier, accuracy = train()
      #output = {"Status": "Success", "Classifier": classifier, "Accuracy": str(accuracy)}
      #print(output)
      #return output
      return templates.TemplateResponse("index.html", {"request": request,"classifier": classifier,"accuracy" : accuracy})

# @app.post("/predict", response_model=NewsClassifierQueryOut, status_code= 200)
# def predict_news_category(query_data: NewsClassifierQueryIn):
#       print(NewsClassifierQueryIn)
#       category = predict(query_data.News)
#       return {"Category":category }

@app.post("/predict_news_category", status_code=200)


def predict_news_category(request: Request,newsText: str = Form(...)):
    query_data = NewsClassifierQueryIn(News = newsText)
    category = predict(query_data.News)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "prediction": category
    })


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8888, reload=True)

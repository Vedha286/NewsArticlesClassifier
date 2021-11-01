import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from model_prediction import predict, load_model

app = FastAPI(title="predictr", docs_url="/")
app.add_event_handler("startup", load_model)

class NewsClassifierTrainIn(BaseModel):
  News: str

class NewsClassifierTrainOut(BaseModel):
    Category: str

@app.post("/predict_news_category", response_model=NewsClassifierTrainOut, status_code= 200)
def predict_news_category(query_data: NewsClassifierTrainIn):
      print(NewsClassifierTrainIn)
      category = predict(query_data.News)
      return {"Category":category }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9999, reload=True)

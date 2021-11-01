import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from model_prediction import predict

# defining the main app
app = FastAPI(title="predictr", docs_url="/")

class NewsClassifierTrainIn(BaseModel):
  News: str
  
class NewsClassifierTrainOut(BaseModel):
    Category: str

@app.post("/predict_news_category", response_model=NewsClassifierTrainOut, status_code=200)
def predict_star(query_data: NewsClassifierTrainIn):
      print(NewsClassifierTrainIn)
      output = {"Category": predict(query_data.News)}
      return output

# Main function to start the app when main.py is called
if __name__ == "__main__":
    # Uvicorn is used to run the server and listen for incoming API requests on 0.0.0.0:8888
    uvicorn.run("main:app", host="0.0.0.0", port=9999, reload=True)

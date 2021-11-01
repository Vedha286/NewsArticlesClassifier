import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from model_training import train, load_model

app = FastAPI(title="trainr", docs_url="/")
app.add_event_handler("startup", load_model)

class NewsClassifierRetrainStatusOut(BaseModel):
    Status: str
    Accuracy: str
    Classifier: str

@app.post("/retrain_news_category", response_model=NewsClassifierRetrainStatusOut, status_code=200)
def retrain_news_category():
      classifier, accuracy = train()
      output = {"Status": "Success", "Classifier": classifier, "Accuracy": str(accuracy)}
      print(output)
      return output

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)

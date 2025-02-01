import os
import requests

def get_sentiment(event, context):
  execute_id = event["responsePayload"]["execute_id"]
  data = event["responsePayload"]["data"]

  hf_api_key = os.getenv("HF_API_KEY")
  url = "https://api-inference.huggingface.co/models/mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"

  payload = { "inputs": [post[2] for post in data] }
  headers = { "Authorization": f"Bearer {hf_api_key}" }
  response = requests.post(url, headers=headers, json=payload)

  if response.status_code == 503:
    headers["x-wait-for-model"] = "true"
    response = requests.post(url, headers=headers, json=payload)

  if response.status_code == 200:
    sentiment_results = response.json()
    if len(sentiment_results) == len(data):
      for i in range(0, len(data)):
        data[i][-1] = sentiment_results[i][0]["label"]

  return {
    "execute_id": execute_id,
    "data": data
  }
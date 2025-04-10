from typing import Union
from fastapi.responses import StreamingResponse
from fastapi import FastAPI
import uvicorn
from fastapi import FastAPI, Depends,Query
import os


from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation
from PIL import Image
import requests
# from google.colab.patches import cv2_imshow
import cv2
import os
from PIL import Image
import requests
from apify_client import ApifyClient
from moviepy import VideoFileClip
from PIL import Image
import requests
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from together import Together
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend (React) to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from React app
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

class Product:
  def __init__(self,keyinput):
    self.keyinput=keyinput
    self.max_tokens=500
    self.temperature=0.7
    self.top_p=0.7
    self.top_k=50
    self.repetition_penalty=1
    self.stop=["<|eot_id|>","<|eom_id|>"]
    self.stream=True
    self.model="meta-llama/Llama-3.3-70B-Instruct-Turbo"
    self.keylist=""
    self.head=""
    self.description=""
    self.keyword=[{
                "role": "system",
                "content": f"""Extract important keywords from the paragraph below that describe the product being mentioned. Each keyword should be separated by a comma (,). Do not include descriptive adjectives or repetitive words with similar meanings. The keywords should focus on the product's characteristics, features, or unique aspects. Only generate the keywords as output, without any additional text.
                Paragraph : {self.keyinput}
                Output : """
        }]
    self.heading=[{
                "role": "system",
                "content": f"""Your task is to generate heading for the product described in the paragraph mentioned below.The product heading must be optimized for Amazon's SEO. Never use any irrelevant information apart from mentioned in the paragraph. Some keywords will be given for example you can use them or any similar keywords. Follow the rules below to create a good heading.
                The output should only be the the product heading.
                Rules :
                Amazon allows sellers 250 characters or your product title.

                They also recommend you use a formula when creating your title.

                Headline Formula

                Product Brand/Description + Line/Collection + Material/Ingredient + Color/Size + Quantity

                Product Title example
                Your particular product may not need to include everything in the formula above.

                A good rule of thumb is without stuffing your product title, include all the information you think your customers need to make a buying decision and try to include keywords based on the paragraph.
                Paragraph : {self.keyinput}
                Output : """
        }]
    self.desc=[{
        "role": "system",
        "content":
        f"""
        Your task is to generate description for the product mentioned in the paragraph given below. Also there is a list of rules that must be followed while creating the description.Below is the set of rules which you must adhere to.Give only the product description as output.
        Rules:
        Include only product-related information, and don’t add misleading facts. Be transparent and honest about the product's features, benefits, and limitations. This will build trust with customers, as well as reduce the likelihood of returns or negative reviews.
Consider the character limit. On Amazon, you can use up to 2,000 characters to tell customers about your product and its features. As long as it fits within these parameters, take advantage of this text length, focusing on explaining the product’s characteristics and benefits.
Write clearly and concisely. Avoid using jargon or technical terms, unless they are essential for understanding the product. Organize information logically, using headings or paragraphs to break up content and improve readability. Additionally, don’t overdo it with your formatting, keeping in mind Amazon doesn’t favor HTML code in descriptions.
Testimonials or quotes of any kind are not allowed. Focus on objective and factual information, as Amazon's guidelines prohibit the use of any testimonials in product descriptions.
Here are some additional recommendations to accompany Amazon's rules.
Don’t include pricing information, as it will quickly become outdated. Instead, reserve that information for the pricing section or special offers section of your listing.
Include relevant keywords naturally in your description. Keywords should flow naturally, making the text informative and helping to increase your item’s search ranking. You also need to avoid keyword stuffing, especially in copywriting, as this can lead to penalties from Amazon.
       Paragraph: {self.keyinput}
       Output:
        """
    }]


  def keywordextractor(self,query,max_tokens=100):
     client = Together(api_key="63b1d2173ee710215020e9fe062a851308f26eb57ee32e62b4098cddbfe2112b")
     self.keyword.append({"role":"user", "content":query})
     response = client.chat.completions.create(
          model=self.model,
          messages=self.keyword,
          max_tokens=self.max_tokens,
          temperature=self.temperature,
          top_p=self.top_p,
          top_k=self.top_k,
          repetition_penalty=self.repetition_penalty,
          stop=self.stop,
          stream=self.stream
     )
     assist=""
     for token in response:
          if hasattr(token, 'choices'):
              assist+=token.choices[0].delta.content
              print(token.choices[0].delta.content, end='', flush=True)

     self.keylist=assist
     self.keyword.append({"role":"assistant","content":assist})

  def headingextractor(self,query,max_tokens=200):
     client = Together(api_key="63b1d2173ee710215020e9fe062a851308f26eb57ee32e62b4098cddbfe2112b")
     self.heading.append({"role":"user", "content":query})
     response = client.chat.completions.create(
          model=self.model,
          messages=self.heading,
          max_tokens=self.max_tokens,
          temperature=self.temperature,
          top_p=self.top_p,
          top_k=self.top_k,
          repetition_penalty=self.repetition_penalty,
          stop=self.stop,
          stream=self.stream
     )
     assist=""
     for token in response:
          if hasattr(token, 'choices'):
              assist+=token.choices[0].delta.content
              print(token.choices[0].delta.content, end='', flush=True)


     self.head=assist
     self.heading.append({"role":"assistant","content":assist})

  def descriptionextractor(self,query,max_tokens=10000):
     client = Together(api_key="63b1d2173ee710215020e9fe062a851308f26eb57ee32e62b4098cddbfe2112b")
     self.desc.append({"role":"user", "content":query})
     response = client.chat.completions.create(
          model=self.model,
          messages=self.desc,
          max_tokens=self.max_tokens,
          temperature=self.temperature,
          top_p=self.top_p,
          top_k=self.top_k,
          repetition_penalty=self.repetition_penalty,
          stop=self.stop,
          stream=self.stream
     )
     assist=""
     for token in response:
          if hasattr(token, 'choices'):
              assist+=token.choices[0].delta.content
              print(token.choices[0].delta.content, end='', flush=True)

     self.description=assist
     self.desc.append({"role":"assistant","content":assist})


# def initilization():
    
class KeywordModel(BaseModel):
    userquestion:str

class DescModel(BaseModel):
    userquestion:str
    descques:str



@app.post("/keyword")
def extractkeyword(q :  KeywordModel):
    pro=Product(q.userquestion)
    pro.keywordextractor("Follow all the instruction properly.")
    print("\nKeywords have been generated")
    pro.headingextractor("Follow all the instruction properly.")
    print("\nHeading has been generated")
    pro.descriptionextractor("Follow all the instruction properly.")
    return {"keyword":pro.keylist,"heading":pro.head,"desc":pro.description}

@app.post('/desc')
def extractkeyword(q : DescModel):
    pro=Product(q.userquestion)
    pro.descriptionextractor(q.descques)
    return {"desc":pro.description}

@app.post('/head')
def extractkeyword(q : DescModel):
    pro=Product(q.userquestion)
    pro.headingextractor(q.descques)
    return {"heading":pro.head}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1" , port=8001, log_level="debug")

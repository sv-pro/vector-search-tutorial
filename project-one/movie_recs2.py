import pymongo
import openai

from settings import MONGODB_URI, OPENAI_API_KEY

# Set your OpenAI API key
openai.api_key = OPENAI_API_KEY

client = pymongo.MongoClient(MONGODB_URI)
db = client.sample_mflix
collection = db.embedded_movies

def generate_embedding(text: str) -> list[float]:

    response = openai.Embedding.create(
        model="text-embedding-ada-002", 
        input=text
    )
    return response['data'][0]['embedding']

query = "imaginary characters from outer space at war"

results = collection.aggregate([
  {"$vectorSearch": {
    "queryVector": generate_embedding(query),
    "path": "plot_embedding",
    "numCandidates": 100,
    "limit": 4,
    "index": "PlotSemanticSearch",
      }}
]);

for document in results:
    print(f'Movie Name: {document["title"]},\nMovie Plot: {document["plot"]}\n')
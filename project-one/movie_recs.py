import pymongo
import requests

from settings import MONGODB_URI, hf_token, embedding_url, UPDATE_EMBEDDINGS

client = pymongo.MongoClient(MONGODB_URI)
db = client.sample_mflix
collection = db.movies
collection_dest = db.movies_hf

def generate_embedding(text: str) -> list[float]:

  print(f"Generating embedding for: {text}")
  
  response = requests.post(
    embedding_url,
    headers={"Authorization": f"Bearer {hf_token}"},
    json={"inputs": text})

  if response.status_code != 200:
    raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")

  return response.json()

query = {"plot_embedding_hf": {"$exists": False}, "plot": {"$exists": True}}
# limit = 50

# UPDATE_EMBEDDINGS is an int, which serves as a flag to update the embeddings and the limit is the number of documents to update
if UPDATE_EMBEDDINGS:
  for doc in collection.find(query).limit(UPDATE_EMBEDDINGS):
    doc['plot_embedding_hf'] = generate_embedding(doc['plot'])
    collection.replace_one({'_id': doc['_id']}, doc)
else:
  print("Set the UPDATE_EMBEDDINGS environment variable to update the embeddings")    

# query = "imaginary characters from outer space at war"
# query = "a love story"
# query = "bandits rob a train"
query = "a dictator comedy"
embedded_query = generate_embedding(query)

# print(f"Query: {query}")
# print(f"Embedded query: {embedded_query}")

# for the aggregation pipeline to work, we need to create a vector index, follow the instructions in the README.md
results = collection.aggregate([
  {"$vectorSearch": {
    "queryVector": embedded_query,
    "path": "plot_embedding_hf",
    "numCandidates": 100,
    "limit": 4,
    # "index": "PlotFullTextSearch",
    "index": "PlotSemanticSearch"
      }}
]);
# numCandidates is the number of candidates to consider for the search

# default dict to convert documents to
# returns "N/A" if key is not found
from collections import defaultdict
results = list(results)
documents = [defaultdict(lambda: "N/A", doc) for doc in results]

print("Results:")

for document in documents:
  # print the title and the plot of the movie
  print(f"{document['title']} - {document['plot']}")
  
if not documents:
  print("No results found")
  # remind the user to create the index
  """
  {
    "mappings": {
      "dynamic": true,
      "fields": {
        "plot_embedding_hf": {
          "type": "knnVector",
          "dimensions": 384,
          "similarity": "dotProduct"
        }
      }
    }
  }
  """

  
  
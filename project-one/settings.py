# import getenv
from os import getenv
# import python dotenv
from dotenv import load_dotenv

# load the .env file
load_dotenv()

MONGODB_URI = getenv("MONGODB_URI")
hf_token = getenv("HF_TOKEN")
embedding_url = getenv("EMBEDDING_URL")

# convert the string to an int
UPDATE_EMBEDDINGS = int(getenv("UPDATE_EMBEDDINGS"))


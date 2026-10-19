"""List the models your API key can use.   Run:  python scripts/list_models.py"""
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

if __name__ == "__main__":
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        sys.exit("OPENAI_API_KEY is not set in your .env file.")
    client = OpenAI(api_key=key, base_url=os.getenv("OPENAI_BASE_URL") or None)
    for model in sorted(client.models.list().data, key=lambda m: m.id):
        print(model.id)
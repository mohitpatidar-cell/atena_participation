import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the model you’ll use — gpt-4-turbo is recommended for structured output
MODEL_NAME = "gpt-4-turbo"

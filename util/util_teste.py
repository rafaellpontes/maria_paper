import json
from openai import OpenAI




#getting env variables
with open('config.json') as f:
    env_variables = json.load(f)
client = OpenAI(api_key=env_variables['openai_key'])

runs = client.beta.threads.runs.list("")





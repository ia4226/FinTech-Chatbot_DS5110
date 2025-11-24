import os
from openai import OpenAI

api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('OPENROUTER_API_KEY')
if not api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable is required for test2deepseek.py")

client = OpenAI(
  base_url=os.environ.get('OPENAI_BASE_URL', 'https://openrouter.ai/api/v1'),
  api_key=api_key,
)

# First API call with reasoning
response = client.chat.completions.create(
  model="x-ai/grok-4.1-fast",
  messages=[
          {
            "role": "user",
            "content": "Who is the president of India?"
          }
        ],
  extra_body={"reasoning": {"enabled": True}}
)

# Extract the assistant message with reasoning_details
response = response.choices[0].message
print(response.content)
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
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
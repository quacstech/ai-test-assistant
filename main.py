from dotenv import load_dotenv
from prompts.system_prompt import SYSTEM_PROMPT
import os
import httpx

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

response = httpx.post(
    "https://api.anthropic.com/v1/messages",
    timeout=120.0,
    headers={
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    },
    json={
        "model": "claude-sonnet-4-5",
        "max_tokens": 4000,
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": input("What would you like to create test scenarios for? > ")}
        ]
    }
)

result = response.json()["content"][0]["text"]
print(result)

with open("output/analysis_result.md", "w") as f:
    f.write(result)

print("\n--- Saved to output/analysis_result.md ---")
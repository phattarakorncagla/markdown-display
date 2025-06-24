import os
import requests
import time

API_URL = "https://router.huggingface.co/novita/v3/openai/chat/completions"
headers = {
    "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
}

import time

def safe_query(payload, retries=3, delay=10):
    for i in range(retries):
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                print("Error parsing response:", e)
                print(response.text)
                return {}
        elif response.status_code == 504:
            print(f"504 Gateway Timeout. Retrying in {delay} sec...")
            time.sleep(delay)
        else:
            print(f"Unexpected error: {response.status_code}")
            print(response.text)
            return {}
    return {"error": "Failed after retries"}

def split_text(text, max_chars=8000):
    chunks = []
    while len(text) > max_chars:
        split_at = text.rfind("\n\n", 0, max_chars)
        if split_at == -1:
            split_at = max_chars
        chunks.append(text[:split_at])
        text = text[split_at:]
    chunks.append(text)
    return chunks

def main():
    input_file = "repository_contents_all_src.txt"
    output_file = "processed_output_all_src.txt"
    model = "deepseek/deepseek-r1-0528"  # Update to a public-access model if needed

    prompt = """You are an expert technical writer specializing in writing documentation for software projects. 
You are tasked with writing a new Specification Document file for the given project.

Here's the name of the project:
<name>
{iphone-app-notification}
</name>

To give you context here is all of the current documentation and source code:
<src>
<<<FILE_CONTENT>>>
</src>

Please format the response using markdown and follow these guidelines:

- Overview of each endpoint, HTTP method, request/response format
- Friendly and educational tone
- Clear, short paragraphs
- Clean code formatting in code fences
- Output should be markdown or plaintext
"""

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = split_text(content, max_chars=10000)

    all_results = []
    start_time = time.time()
    for i, chunk in enumerate(chunks):
        print(f"[*] Sending chunk {i+1}/{len(chunks)}...")
        full_prompt = prompt.replace("<<<FILE_CONTENT>>>", chunk)

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        }

        response = safe_query(payload)
        if "choices" in response:
            message = response["choices"][0]["message"]["content"]
            all_results.append(f"\n## Chunk {i+1}\n{message}")
        else:
            all_results.append(f"\n## Chunk {i+1}\n[No output or error]\n{response}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(all_results))

    elapsed = time.time() - start_time
    minutes, seconds = divmod(elapsed, 60)
    print(f"[*] Done! Elapsed time: {int(minutes)} min {int(seconds)} sec")
    print(f"[*] Finish at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

if __name__ == "__main__":
    main()

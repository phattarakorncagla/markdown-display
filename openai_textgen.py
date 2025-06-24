import time
import openai
from openai import OpenAI
from openai.types.chat import ChatCompletion

client = OpenAI(  
    api_key="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", 
    base_url="https://openrouter.ai/api/v1" 
)

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

def safe_openai_call(payload, retries=3, delay=10):
    for attempt in range(retries):
        try:
            response: ChatCompletion = client.chat.completions.create(**payload)
            return response
        except Exception as e:
            print(f"[!] Error: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                return {"error": str(e)}
    return {"error": "Failed after retries"}

def main():
    input_file = "repository_contents_all_src.txt"
    output_file = "processed_output_all_src.txt"
    model = "deepseek/deepseek-r1-0528:free" 

    prompt_template = """You are an expert technical writer specializing in writing documentation for software projects. 
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

    chunks = split_text(content, max_chars=8000)

    all_results = []
    start_time = time.time()

    for i, chunk in enumerate(chunks):
        print(f"[*] Processing chunk {i+1}/{len(chunks)}...")
        full_prompt = prompt_template.replace("<<<FILE_CONTENT>>>", chunk)

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": full_prompt}
            ],
            "temperature": 0.7,
        }

        response = safe_openai_call(payload)

        if isinstance(response, dict) and "error" in response:
            all_results.append(f"\n## Chunk {i+1}\n[Error]: {response['error']}")
        else:
            message = response.choices[0].message.content
            all_results.append(f"\n## Chunk {i+1}\n{message}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(all_results))

    elapsed = time.time() - start_time
    minutes, seconds = divmod(elapsed, 60)
    print(f"[*] Done! Elapsed time: {int(minutes)} min {int(seconds)} sec")
    print(f"[*] Finished at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

if __name__ == "__main__":
    main()

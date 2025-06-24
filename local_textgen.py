import os
import subprocess
import time

def run_local_model(model: str, prompt: str, content: str) -> str:
    try:
        full_input = f"{prompt}\n\n{content}"

        result = subprocess.run(
            ["ollama", "run", model],
            input=full_input.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=2000 
        )

        if result.returncode != 0:
            print("Ollama error:", result.stderr.decode())
            return ""

        return result.stdout.decode("utf-8")

    except Exception as e:
        print("Failed to run local model:", e)
        return ""

def split_text(text, max_chars=5000):  # Reduce size for safer local inference
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
    input_file = "repository_contents.txt"
    output_file = "processed_output_new.txt"
    model = "DeepSeek-R1-0528-Qwen3-8B-Q4_K_M:latest" 

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

    chunks = split_text(content, max_chars=5000)

    all_results = []
    start_time = time.time()
    for i, chunk in enumerate(chunks):
        print(f"[*] Running local model on chunk {i+1}/{len(chunks)}...")
        full_prompt = prompt.replace("<<<FILE_CONTENT>>>", chunk)
        result = run_local_model(model, prompt, chunk)

        if result:
            all_results.append(f"\n## Chunk {i+1}\n{result}")
        else:
            all_results.append(f"\n## Chunk {i+1}\n[No output or error]")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(all_results))

    elapsed = time.time() - start_time
    minutes, seconds = divmod(elapsed, 60)
    print(f"[*] Done! Elapsed time: {int(minutes)} min {int(seconds)} sec")
    print(f"[*] Finish at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

if __name__ == "__main__":
    main()

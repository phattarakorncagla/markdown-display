import time
from datetime import datetime
from ollama import chat

def split_text(text, max_chars=8000):
    chunks = []
    while len(text) > max_chars:
        split_at = text.rfind("\n\n", 0, max_chars)
        if split_at == -1:
            split_at = max_chars
        chunks.append(text[:split_at].strip())
        text = text[split_at:].strip()
    chunks.append(text)
    return chunks

def main():
    input_file = "input/test.txt"
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output/ollama_output_{date_str}.txt"
    model = "Code-Summary-Llama-3.2-3B-Instruct.Q4_K_S:latest" 

    prompt_template = """You are an expert technical writerspecializing in writing documentation for software projects. 
    Document must have functions, endpoints, and explain request/response if any. Be clear, concise, and informative.
    Create clean, markdown-formatted technical documentation from the source code below in English.
    """

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = split_text(content, max_chars=8000)
    all_results = []
    start_time = time.time()

    for i, chunk in enumerate(chunks):
        print(f"[*] Processing chunk {i+1}/{len(chunks)}...")
        full_prompt = prompt_template.replace("<<<FILE_CONTENT>>>", chunk)

        try:
            response = chat(model=model, messages=[
                {"role": "user", "content": full_prompt}
            ])
            all_results.append(f"\n## Chunk {i+1}\n{response.message.content}")
        except Exception as e:
            print(f"[!] Error in chunk {i+1}: {e}")
            all_results.append(f"\n## Chunk {i+1}\n[Error: {e}]")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(all_results))

    elapsed = time.time() - start_time
    print(f"[*] Done! Output saved to {output_file}")
    print(f"[*] Elapsed time: {int(elapsed // 60)} min {int(elapsed % 60)} sec")

if __name__ == "__main__":
    main()

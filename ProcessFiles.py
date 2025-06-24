import subprocess
import time

def run_ollama_model(model: str, prompt: str, content: str) -> str:
    try:
        # Combine prompt and content
        full_input = f"{prompt}\n\n{content}"

        # Call Ollama with subprocess
        result = subprocess.run(
            ["ollama", "run", model],
            input=full_input.encode('utf-8'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=1000  # Timeout after 16 minutes 40 seconds
        )

        if result.returncode != 0:
            print("Ollama error:", result.stderr.decode())
            return ""

        return result.stdout.decode('utf-8')

    except Exception as e:
        print("Failed to run Ollama:", e)
        return ""

def split_text(text, max_chars=5000):
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
    output_file = "processed_output.txt"
    model = "gemma-3-document-writer.q8_0:latest"  # Change this if you're using a different model

    # Your custom prompt
    prompt = """You are an expert technical writer specializing in writing documentation for software projects. 
You are tasked with writing a new Specification Document file for the given project. 
Your goal is to create an informative documentation for software engineers.

First, here's the name of the project:
<name>
{iphone-app-notification}
</name>

To give you context here is all of the current documentation and source code for the project that you need to summerize
<src>
 is in the file repository_contents.txt.
</src>


When writing the text file, follow these guidelines:

1. Structure:
   - Overview of each endpoint for each and every function
		HTTP methods
		Request/response formats
		

2. Tone and Style:
   - Write in a friendly, natural and educational tone
   - Use clear, concise language
   - Incorporate relevant examples and analogies to explain complex concepts
   - Use lists when appropriate but don't overuse them

3. Text Formatting:
   - The output of this document will be Markdown
   - Use headers (H1 for title, H2 for main sections, H3 for subsections)
   - Keep paragraphs short (3-5 sentences)
   - Proofread for grammar, spelling, and clarity

4. Code Formatting:
    - Use clean and concise code examples
    - Avoid including import statements or package declarations for brevity
    - Use consistent indentation (prefer spaces to tabs)
    - Use meaningful variable and function names
    - Break long lines of code for readability
    - If showing output, clearly separate it from the code
    - Include a brief explanation before and/or after each code block

5. Output:
   - The output can be in markdown format or normal text file format
   - Use code fences when possible and the correct language definiton


Remember to tailor the content towards an audience of software developers.
"""

    # Read all file contents
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print("[*] Sending content to Ollama...")
    start_time = time.time()


    print("[*] Splitting content into chunks...")
    chunks = split_text(content, max_chars=8000) 

    all_results = []
    for i, chunk in enumerate(chunks):
        print(f"[*] Sending chunk {i+1}/{len(chunks)}...")
        result = run_ollama_model(model, prompt, chunk)
        if result:
            all_results.append(f"\n## Chunk {i+1}\n{result}")
        else:
            all_results.append(f"\n## Chunk {i+1}\n[No output]")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(all_results))

    end_time = time.time()
    elapsed = end_time - start_time

    minutes, seconds = divmod(elapsed, 60)
    print(f"[*] Time elapsed: {int(minutes)} minutes {int(seconds)} seconds")

if __name__ == "__main__":
    main()

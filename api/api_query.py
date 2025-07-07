import anthropic
import json
import os
import time
from tqdm import tqdm

# API setup
client = anthropic.Anthropic(api_key="") # Your api key here, fill here
model_name = "claude-sonnet-4-20250514"

# System prompt
system_prompt = (
    "You are an expert evaluator. Determine if the provided answer to the question is correct or incorrect, "
    "then clearly state the reason for your decision. Respond in valid JSON with 'correct' (true or false) and 'reason'."
)

# File paths
base_path = r"" # Your base path, fill here
input_file = os.path.join(base_path, "questions_with_paragraphs.txt")
checkpoint_file = os.path.join(base_path, "checkpoint.json")
output_file = os.path.join(base_path, "evaluated_results.json")

# JSON parsing function
def parse_json_response(response_text):
    """
    Claude sometimes sends the response in a code block (` ```json ... ```).
    This function cleans up code blocks and extra characters and parses the JSON.
    """
    txt = response_text.strip()
    # Remove code block if it exists
    if txt.startswith("```"):
        txt = txt.split("```", 2)[1] if "```" in txt else txt
    # Find only the first valid JSON
    first_curly = txt.find("{")
    last_curly = txt.rfind("}")
    if first_curly >= 0 and last_curly >= 0:
        txt = txt[first_curly:last_curly + 1]
    try:
        return json.loads(txt)
    except Exception as e:
        return None

# --- Safely read corrupted lines ---
questions_answers = []
with open(input_file, "r", encoding="utf-8") as f:
    raw_data = f.read().strip().split("\n\n")

for idx, item in enumerate(raw_data):
    lines = [x for x in item.strip().split("\n") if x.strip()]
    if len(lines) < 2:
        print(f"WARNING: Skipping item #{idx+1}, not enough lines.")
        continue
    question = lines[-2]
    answer = lines[-1].replace("Answer: ", "")
    paragraph = " ".join(lines[:-2])
    questions_answers.append({"paragraph": paragraph, "question": question, "answer": answer})

# --- Safely read the checkpoint file ---
try:
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            results = json.load(f)
            if not isinstance(results, list):
                print("Checkpoint file is corrupted. Starting from scratch.")
                results = []
    else:
        results = []
except Exception as e:
    print(f"Checkpoint could not be read: {e}. Starting from scratch.")
    results = []

# --- API Query and Retry Mechanism ---
def query_claude_with_retry(prompt, system_prompt, max_retries=3, wait_sec=5):
    """
    Queries Claude via API, retries on rate limit or parse errors.
    """
    for attempt in range(1, max_retries+1):
        try:
            response = client.messages.create(
                model=model_name,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
                system=system_prompt
            )
            # Try to parse JSON
            parsed = parse_json_response(response.content[0].text)
            if parsed is not None and isinstance(parsed, dict) and "correct" in parsed and "reason" in parsed:
                return parsed, response.content[0].text
            else:
                raise ValueError("JSON parse/format error")
        except Exception as ex:
            print(f"API/parse error (attempt {attempt}/{max_retries}): {ex}")
            if attempt < max_retries:
                time.sleep(wait_sec)
            else:
                return {"correct": None, "reason": "API or JSON parse error."}, None

# --- Main Query Loop ---
for qa in tqdm(questions_answers[len(results):], desc="Evaluating"):
    prompt = f"{qa['paragraph']}\n\nQuestion: {qa['question']}\nAnswer: {qa['answer']}\n\nIs this answer correct, and why?"

    result, raw_response = query_claude_with_retry(prompt, system_prompt, max_retries=3, wait_sec=5)
    qa.update(result)
    # Also save the original Claude response (for debugging)
    qa["raw_response"] = raw_response
    results.append(qa)

    # Checkpoint save
    with open(checkpoint_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    # A short wait to avoid overloading the API (reduces the risk of rate limiting)
    time.sleep(3)

# --- Final save ---
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# --- Statistics ---
total_questions = len(results)
correct_answers = sum(1 for r in results if r.get("correct") is True)
incorrect_answers = sum(1 for r in results if r.get("correct") is False)
none_answers = sum(1 for r in results if r.get("correct") is None)

print(f"\nEvaluation complete and saved.")
print(f"Total questions evaluated: {total_questions}")
print(f"Correct answers: {correct_answers}")
print(f"Incorrect answers: {incorrect_answers}")
print(f"Unparsed/unknown (None) answers: {none_answers}")

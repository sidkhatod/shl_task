import time
import json
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-flash-latest")

LAST_CALL = 0

def gemini_generate(prompt: str) -> str:
    global LAST_CALL

    now = time.time()
    elapsed = now - LAST_CALL

    if elapsed < 60:
        time.sleep(60 - elapsed)

    LAST_CALL = time.time()
    return model.generate_content(prompt).text


def parse_query_with_gemini(query: str) -> dict:
    prompt = (
        "Extract structured hiring intent from the query below.\n\n"
        f"Query: \"{query}\"\n\n"
        "Return JSON with:\n"
        "- hard_skills (list)\n"
        "- soft_skills (list)\n"
        "- desired_test_types (list of full names)\n"
        "- max_duration_minutes (integer or null)"
    )

    try:
        response = gemini_generate(prompt)
        return json.loads(response)
    except Exception:
        return {
            "hard_skills": [],
            "soft_skills": [],
            "desired_test_types": [],
            "max_duration_minutes": None
        }

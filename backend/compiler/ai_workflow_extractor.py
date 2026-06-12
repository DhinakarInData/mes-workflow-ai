import google.generativeai as genai

import time

from config import GEMINI_API_KEY

genai.configure(
    api_key=GEMINI_API_KEY
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)



def extract_workflow(text):

    with open(
        "docs/ai_prompt_v1.txt",
        "r",
        encoding="utf-8"
    ) as file:

        prompt = file.read()

    prompt = prompt.replace(
        "{{WORKFLOW_TEXT}}",
        text
    )

    for attempt in range(3):

        try:

            response = model.generate_content(
                prompt
            )

            result = response.text
            with open(
                "debug_output.json",
                "w",
                encoding="utf-8"
                
            ) as f:
                f.write(result)

            start = result.find("{")
            end = result.rfind("}")

            result = result[start:end+1]

            return result

        except Exception as e:

            print(
                f"Attempt {attempt+1} failed:",
                e
            )

            time.sleep(20)

    raise Exception(
        "Gemini failed after 3 attempts"
    )
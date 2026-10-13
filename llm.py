
import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def get_answer(prompt):
    system_prompt = """
You are an AI Student Assistant for educational purposes.

Your task is to generate study notes and multiple-choice quizzes
based on the student's input.

GENERAL RULES:
- Use simple, clear English.
- Explain concepts in a student-friendly way.
- Follow the requested topic, level, and format.
- Include relevant examples when useful.
- Do not add unrelated information.
- Do not behave as a conversational chatbot.

FOR STUDY NOTES:
- Provide a clear title.
- Include a simple definition.
- Explain important concepts using headings.
- Use bullet points and examples.
- Include a short conclusion or revision points.

FOR QUIZZES:
- Generate the requested number of questions.
- Provide four options for each question.
- Ensure only one option is correct.
- Include the correct answer and a short explanation.
- If JSON is requested, return valid JSON only
  in the exact format requested by the user.
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=f"""
{system_prompt}

Student's request:
{prompt}
"""
            )
            return response.text

        except Exception as e:
            if "503" in str(e) and attempt < 2:
                time.sleep(5)
            else:
                return (
                    "Gemini is temporarily busy or the request failed. "
                    "Please check your API configuration and try again."
                )

import flask
from flask import Flask, request, render_template
import openai
from openai.error import RateLimitError
from dotenv import load_dotenv
import os
from functools import lru_cache

load_dotenv()  # This loads the environment variables from .env
openai_api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
app.config["ENV"] = "development"
openai.api_key = openai_api_key

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

document_text = extract_text_from_txt('The Dandelion Girl.txt')

def process_initial_question(question):
    try:
        prompt = f"Is the following question clear and specific enough to answer? Question: {question}"
        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=50)
        is_clear = "Yes" in response.choices[0].text.strip()
        return is_clear
    except RateLimitError:
        return False, "API rate limit exceeded. Please try again later."
    
@lru_cache(maxsize=32)
def summarize_document(document_text):
    # summarize the document
    prompt = "Please summarize the following text:\n\n" + document_text
    response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=300)
    return response.choices[0].text.strip()

def extract_key_section(document_text, question):
    # extract key sections relevant to the question
    prompt = f"Extract the key section from the document relevant to this question: {question}\n\nDocument:\n{document_text}"
    response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=200)
    return response.choices[0].text.strip()

def generate_answer(question, document_text):
    # Placeholder for the logic from langchain_QA.ipynb
    # This should generate an answer using GPT-3 and the document text
    return "Answer from langchain_QA logic."

@app.route('/', methods=['GET', 'POST'])
def index():
    answer, feedback_prompt, error_message = '', '', ''
    if request.method == 'POST':
        user_question = request.form['question']
        is_clear, response = process_initial_question(user_question)
        if is_clear:
            user_question = request.form['question']
            document_text = extract_text_from_txt('The Dandelion Girl.txt')  # Load your document here
            document_summary = summarize_document(document_text)
            relevant_section = extract_key_section(document_summary, user_question)
            # Use the relevant section to generate an answer
            answer = generate_answer(user_question, relevant_section)
        elif response:
            feedback_prompt = response
        else:
            error_message = "API rate limit exceeded. Please try again later."
    return render_template('index.html', answer=answer, feedback_prompt=feedback_prompt, error_message=error_message)

@app.route('/feedback', methods=['POST'])
def feedback():
    user_feedback = request.form['feedback']
    # Placeholder for processing feedback
    return "Thank you for your feedback!"

if __name__ == '__main__':
    app.run(debug=True)

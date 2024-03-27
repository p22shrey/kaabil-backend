from flask import Flask, jsonify, request
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/api/subtitles-questions', methods=['POST'])
def get_subtitles_and_questions():
    video_id = request.json['videoId']
    subtitles = YouTubeTranscriptApi.get_transcript(video_id)
    transcript = str(subtitles)
    
    questions = generate_questions(transcript)
    print(questions)
    return jsonify({"questions": questions, "transcript": transcript})

@app.route('/api/feedback', methods=['POST'])
def get_feedback():
    user_response = request.json['userResponse']
    question = request.json['question']
    transcript = request.json['transcript']
    
    feedback = generate_feedback(user_response, question, transcript)
    # Store the question, user response, and feedback in the database (future implementation)
    
    return jsonify(feedback)

def generate_questions(transcript):
    model = "gpt-3.5-turbo-1106"
    messages = [
        {"role": "system", "content": '''
         You are a helpful assistant who generates a list of UPSC style questions to test attentiveness and knowledge gain for a user watching a video with the given transcript.
         The user needs to be asked a question roughly every 150 seconds based on the information revealed in the video uintil the time of the question being asked.
         You will provide a list of questions and the appropriate timestamps for the user to pause the video and answer the question. All timestamps indicate the time in seconds from the start of the video.
         Example output: {"questions": [{"time": "16.37", "question": "Who is the protaganist?"}, {"time": "134.86", "question": "What was the protaganist's main motivation?"}]}
         Output only the JSON without any extra explanation or language indicators.
         '''},
        {"role": "user", "content": transcript}
    ]
    response_format = {"type": "json_object"}
    response = client.chat.completions.create(model=model, messages=messages, response_format=response_format)
    questions = response.choices[0].message.content
    return questions

def generate_feedback(user_response, question, transcript):
    model = "gpt-3.5-turbo"
    messages = [
        {"role": "system", "content": "Provide some feedback based on the following context. You have a transcript, a question, and a user response."},
        {"role": "user", "content": f"{transcript}\n{question}\n{user_response}"}
    ]
    response = client.chat.completions.create(model=model, messages=messages)
    feedback = response.choices[0].message.content
    return feedback

if __name__ == '__main__':
    app.run(debug=True)
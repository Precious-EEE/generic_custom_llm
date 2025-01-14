import os
import logging
from flask import Flask, Blueprint, request, Response, json
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
custom_llm = Blueprint('custom_llm', __name__)
client = OpenAI(api_key="OPENAI_API_KEY")


def generate_streaming_response(data):
    for message in data:
        json_data = message.model_dump_json()
        logger.info(f"JSON data: {json.dumps(json_data, indent=2)}")
        yield f"data: {json_data}\n\n"


@custom_llm.route('/chat/completions', methods=['POST'])
def openai_advanced_custom_llm_route():
    request_data = request.get_json()

    # Use this if you want to see the request
    # logger.info(f"Request data: {json.dumps(request_data, indent=2)}")
    streaming = request_data.get('stream', False)

    del request_data['call']
    del request_data['metadata']

    if streaming:
        chat_completion_stream = client.chat.completions.create(**request_data)

        return Response(generate_streaming_response(chat_completion_stream),
                        content_type='text/event-stream')
    else:
        # Simulate a non-streaming response
        chat_completion = client.chat.completions.create(**request_data)
        return Response(chat_completion.model_dump_json(),
                        content_type='application/json')


# Add a default home page
@app.route('/')
def home():
    return "<h1>Welcome to the Generic Customer Service Support LLM</h1><p>Use the endpoint '/chat/completions' for interactions.</p>"


app.register_blueprint(custom_llm)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

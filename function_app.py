import azure.functions as func
import logging
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="AudioTranscriptor")
def AudioTranscriptor(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    # Get environment variables
    subscription_key = os.getenv("AZURE_SPEECH_KEY")

    try:
        # Get the audio file from the request
        audio_file = req.files.get('file')
        if not audio_file:
            return func.HttpResponse("Please pass an audio file in the request", status_code=400)

        # Prepare the API call to Azure Speech to Text service
        endpoint = f"https://eastus.api.cognitive.microsoft.com/speechtotext/transcriptions:transcribe?api-version=2024-05-15-preview"

        headers = {
            'Accept': 'application/json',
            'Ocp-Apim-Subscription-Key': subscription_key
        }

        files = {
            'audio': (audio_file.filename, audio_file.stream, audio_file.content_type),
            'definition': (None, '{"locales":["en-US"],"profanityFilterMode":"None","channels":[0,1]}')
        }

        # Make the API call
        response = requests.post(endpoint, headers=headers, files=files)
        response.raise_for_status()

        # Return the API response
        return func.HttpResponse(response.text, mimetype="application/json", status_code=response.status_code)

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(f"An error occurred: {str(e)}", status_code=500)

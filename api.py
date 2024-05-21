import os
import requests

def _get_base_url():
    return "http://localhost:8111/api/v1"

def _get_headers():
    return {"Authorization": f"Bearer {os.getenv('NEXTGPT_API_KEY')}"}


def create_chat_completion(chat_payload, session_id):
    headers = _get_headers()
    url = f"{_get_base_url()}/chat/completions?debug=True"
    if session_id:
        url += f"&session_id={session_id}"
    return requests.post(url, json=chat_payload, headers=headers)

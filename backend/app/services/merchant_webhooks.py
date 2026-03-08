import requests


def send_webhook(url, payload):

    try:

        response = requests.post(url, json=payload, timeout=3)

        return {"status": response.status_code}

    except Exception as e:

        return {"error": str(e)}
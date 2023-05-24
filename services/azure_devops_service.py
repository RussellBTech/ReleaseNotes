import requests
import base64

def get_headers(pat):
    credentials = f":{pat}"
    credentials = base64.b64encode(credentials.encode()).decode()
    return {
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/json'
    }

def validate_org_url(pat, org_url):
    try:
        headers = get_headers(pat)
        response = requests.get(
            f"{org_url}/_apis/projects?api-version=6.0", headers=headers)
        if response.status_code != 200:
            return False, response.json().get('message', 'Unknown error')

        return True, ''

    except requests.exceptions.RequestException as e:
        return False

def validate_project(pat, org_url, project_name):
    headers = get_headers(pat)
    url = f"{org_url}/_apis/projects/{project_name}?api-version=6.1-preview.4"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return False

    return True

def get_list(pat, url):
    headers = get_headers(pat)
    response = requests.get(url, headers=headers)
    return response.json().get('value', [])

def get_item(pat, url):
    headers = get_headers(pat)
    response = requests.get(url, headers=headers)
    return response.json()

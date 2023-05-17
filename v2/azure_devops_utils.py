import requests
import base64

def create_headers(pat):
    credentials = f":{pat}"
    credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/json'
    }
    return headers

def get_pull_requests(orgUrl, repository, headers):
    baseApiUrl = f"{orgUrl}/_apis/git/repositories"
    pullRequestApiUrl = f"{baseApiUrl}/{repository}/pullRequests"
    pullRequestsTemp = requests.get(f"{pullRequestApiUrl}?searchCriteria.sourceRefName=refs/heads/dev&searchCriteria.targetRefName=refs/heads/master", headers=headers).json().get('value', [])
    return pullRequestsTemp

def get_work_items(orgUrl, repository, pullRequestId, headers):
    baseApiUrl = f"{orgUrl}/_apis/git/repositories"
    pullRequestApiUrl = f"{baseApiUrl}/{repository}/pullRequests"
    workItemsUrl = f"{pullRequestApiUrl}/{pullRequestId}/workitems"
    workItems = requests.get(workItemsUrl, headers=headers).json().get('value', [])
    return workItems

import time
import requests
import base64
import webbrowser
import tempfile
import os

from kirby import get_kirby_line


def generate_release_notes(pat, orgUrl, projectName, repositoryNames):
    if not validate_org_url(pat, orgUrl):
        return None, "Invalid PAT or Organization URL, check both"
    if not validate_project(pat, orgUrl, projectName):
        return None, f"Project '{projectName}' not found"

    baseApiUrl = f"{orgUrl}/{projectName}/_apis/git/repositories"
    workItemApiUrl = f"{orgUrl}/{projectName}/_apis/wit/workitems"

    # Creating header for API calls
    headers = get_headers(pat)

    # Initializing variables
    workItemsDict = {}
    releaseNotes = "<html><body>"

    # Get all work items in every repository for every pull request
    for repository in repositoryNames:
        pullRequestApiUrl = f"{baseApiUrl}/{repository}/pullRequests"
        pullRequestsTemp = requests.get(
            f"{pullRequestApiUrl}?searchCriteria.sourceRefName=refs/heads/dev&searchCriteria.targetRefName=refs/heads/master", headers=headers).json().get('value', [])
        if not pullRequestsTemp:
            # If pullRequestsTemp is empty, fetch the most recent completed pull request
            pullRequestsTemp = requests.get(
                f"{pullRequestApiUrl}?searchCriteria.status=completed&searchCriteria.sourceRefName=refs/heads/dev&searchCriteria.targetRefName=refs/heads/master&$top=1&$orderby=createdDate desc", headers=headers).json().get('value', [])

        for pullRequest in pullRequestsTemp:
            pullRequestId = pullRequest.get('pullRequestId', '')
            if pullRequestId:
                workItems = requests.get(
                    f"{pullRequestApiUrl}/{pullRequestId}/workitems", headers=headers).json().get('value', [])
                if workItems:
                    releaseNotes += f'<p style="color:blue;">&#9679; {repository} &#9679;</p> - Pull Request {pullRequestId}: {pullRequest["title"]}<br>'
                    releaseNotes += f'<p>{get_kirby_line()}</p>'
                    for workItem in workItems:
                        if workItem['id'] not in workItemsDict:
                            workItemsDict[workItem['id']] = workItem
                            workItemUrl = f"{workItemApiUrl}/{workItem['id']}"
                            workItemDetail = requests.get(
                                workItemUrl, headers=headers).json()
                            workItemTitle = workItemDetail['fields']['System.Title']
                            # Human readable URL
                            humanReadableWorkItemUrl = f"{orgUrl}/{projectName}/_workitems/edit/{workItem['id']}"
                            # Now, include the workItemId and the workItemTitle as part of the link
                            releaseNotes += f'- <a href="{humanReadableWorkItemUrl}">{workItem["id"]} - {workItemTitle}</a><br>'

                    releaseNotes += f'<p>{get_kirby_line()}</p><br>'

    releaseNotes += "</body></html>"

    return releaseNotes, ""


def open_release_notes(releaseNotes):
    # Save the release notes to a temporary HTML file
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
        f.write(releaseNotes)
    temp_file_name = f.name

    # Open the temporary HTML file in the default web browser
    webbrowser.open('file://' + os.path.realpath(temp_file_name))

    # Pause for 2 seconds to give the web browser time to open the file
    time.sleep(2)

    # Delete the temporary file
    os.unlink(temp_file_name)


def validate_org_url(pat, org_url):
    # Validate the provided Organization URL using a simple GET request.
    try:
        headers = get_headers(pat)

        # We make a GET request to the Azure DevOps REST API's Core API to fetch the organization details
        response = requests.get(
            f"{org_url}/_apis/projects?api-version=6.0", headers=headers)
        # If the status code is not 200 (OK), then the URL is invalid
        if response.status_code != 200:
            return False, response.json().get('message', 'Unknown error')

        return True, ''

    except requests.exceptions.RequestException as e:
        return False


def validate_project(pat, org_url, project_name):
    # Validate the provided project name using Azure DevOps REST API
    headers = get_headers(pat)

    url = f"{org_url}/_apis/projects/{project_name}?api-version=6.1-preview.4"

    response = requests.get(url, headers=headers)

    # If the status code is not 200 (OK), then the project is invalid
    if response.status_code != 200:
        return False

    return True


def get_headers(pat):
    # Validate the provided project name using Azure DevOps REST API
    credentials = f":{pat}"
    credentials = base64.b64encode(credentials.encode()).decode()
    return {
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/json'
    }

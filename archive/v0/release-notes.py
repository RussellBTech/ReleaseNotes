import time
import requests
import base64
import webbrowser
import tempfile
import os
from kirby import get_kirby_line

pat = ""  # Replace with your own personal access token
orgUrl = "https://dev.azure.com/cmgfidev"
projectName = "CLEAR"  # Replace with your project name
repositoryNames = ["CMG.CLEAR2.UI", "CMG.EPS.Loan", "CMG.CLEAR2.API"]  # Add your repository names here

baseApiUrl = f"{orgUrl}/{projectName}/_apis/git/repositories"
workItemApiUrl = f"{orgUrl}/{projectName}/_apis/wit/workitems"

# Creating header for API calls
credentials = f":{pat}"
credentials = base64.b64encode(credentials.encode()).decode()
headers = {
    'Authorization': f'Basic {credentials}',
    'Content-Type': 'application/json'
}

workItemsDict = {}

releaseNotes = "<html><body>"

for repository in repositoryNames:
    pullRequestApiUrl = f"{baseApiUrl}/{repository}/pullRequests"
    pullRequestsTemp = requests.get(f"{pullRequestApiUrl}?searchCriteria.sourceRefName=refs/heads/dev&searchCriteria.targetRefName=refs/heads/master", headers=headers).json().get('value', [])

    for pullRequest in pullRequestsTemp:
        pullRequestId = pullRequest.get('pullRequestId', '')
        if pullRequestId:
            workItems = requests.get(f"{pullRequestApiUrl}/{pullRequestId}/workitems", headers=headers).json().get('value', [])
            if workItems:
                releaseNotes += f'<p style="color:blue;">&#9679; {repository} &#9679;</p> - Pull Request {pullRequestId}: {pullRequest["title"]}<br>'
                releaseNotes += f'<p>{get_kirby_line()}</p>'
                for workItem in workItems:
                    if workItem['id'] not in workItemsDict:
                        workItemsDict[workItem['id']] = workItem
                        workItemUrl = f"{workItemApiUrl}/{workItem['id']}"
                        workItemDetail = requests.get(workItemUrl, headers=headers).json()
                        workItemTitle = workItemDetail['fields']['System.Title']
                        # Human readable URL
                        humanReadableWorkItemUrl = f"{orgUrl}/{projectName}/_workitems/edit/{workItem['id']}"
                        # Now, include the workItemId and the workItemTitle as part of the link
                        releaseNotes += f'- <a href="{humanReadableWorkItemUrl}">{workItem["id"]} - {workItemTitle}</a><br>'
                releaseNotes += f'<p>{get_kirby_line()}</p><br>'

releaseNotes += "</body></html>"

# Save the release notes to a temporary HTML file
with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
    f.write(releaseNotes)
temp_file_name = f.name

# Open the temporary HTML file in the default web browser
webbrowser.open('file://' + os.path.realpath(temp_file_name))

#pause for 1 seconds
#wait for user to close the browser
input("Press Enter to continue...")
time.sleep(5)
os.unlink(temp_file_name)  # Delete the temporary file

# release_notes.py

from datetime import date, datetime
import time
import webbrowser
import tempfile
import os
from services.azure_devops_service import validate_org_url, validate_project, get_list, get_list, get_item

from kirby import get_kirby_line

def generate_release_notes(pat, orgUrl, projectName, repositoryNames, startDate):
    if not validate_org_url(pat, orgUrl):
        return None, "Invalid PAT or Organization URL, check both"
    if not validate_project(pat, orgUrl, projectName):
        return None, f"Project '{projectName}' not found"

    baseApiUrl = f"{orgUrl}/{projectName}/_apis/git/repositories"
    workItemApiUrl = f"{orgUrl}/{projectName}/_apis/wit/workitems"

    # Initializing variables
    workItemsDict = {}
    releaseNotes = "<html><body>"

    # Get all work items in every repository for every pull request
    for repository in repositoryNames:
        pullRequestApiUrl = f"{baseApiUrl}/{repository}/pullRequests"
        pullRequestsTemp = get_list(pat, f"{pullRequestApiUrl}?searchCriteria.status=completed&searchCriteria.targetRefName=refs/heads/master")
        if not pullRequestsTemp:
            # If pullRequestsTemp is empty, fetch the most recent completed pull request
            pullRequestsTemp = get_list(pat, f"{pullRequestApiUrl}?searchCriteria.status=completed&searchCriteria.targetRefName=refs/heads/master&$orderby=createdDate desc")
        
        pullRequestsTemp = [pr for pr in pullRequestsTemp if datetime.strptime(pr['creationDate'][:10], '%Y-%m-%d').date() >= startDate]

        for pullRequest in pullRequestsTemp:
            pullRequestId = pullRequest.get('pullRequestId', '')
            if pullRequestId:
                # Create pull request URL
                pullRequestUrl = f"{orgUrl}/{projectName}/_git/{repository}/pullrequest/{pullRequestId}"
                workItems = get_list(pat, f"{pullRequestApiUrl}/{pullRequestId}/workitems")
                if workItems:
                    releaseNotes += f'<p style="color:blue;">&#9679; {repository} &#9679;</p> - <a href="{pullRequestUrl}" target="_blank">Pull Request {pullRequestId}: {pullRequest["title"]}</a><br>'
                    releaseNotes += f'<p>{get_kirby_line()}</p>'
                    for workItem in workItems:
                        if workItem['id'] not in workItemsDict:
                            workItemsDict[workItem['id']] = workItem
                            workItemUrl = f"{workItemApiUrl}/{workItem['id']}"
                            workItemDetail = get_item(pat, workItemUrl)
                            workItemTitle = workItemDetail['fields']['System.Title']
                            # Human readable URL
                            humanReadableWorkItemUrl = f"{orgUrl}/{projectName}/_workitems/edit/{workItem['id']}"
                            # Now, include the workItemId and the workItemTitle as part of the link
                            releaseNotes += f'- <a href="{humanReadableWorkItemUrl}" target="_blank">{workItem["id"]} - {workItemTitle}</a><br>'

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

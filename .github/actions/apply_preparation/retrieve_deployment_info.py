import json
import os
import argparse
import http.client

def make_github_request(url, github_token):
    # Create a connection to the GitHub API server
    conn = http.client.HTTPSConnection("api.github.com")

    # GitHub personal access token for authentication
    
    # Prepare headers with authorization
    headers = {
        'User-Agent': 'TheTacosBot',
        'Authorization': f'Bearer {github_token}',
    }

    # Resource URL (for example, fetching user data for a specific username)
    resource = f"/repos/{repository}/deployments?environment={environment}"

    # Send a GET request
    conn.request("GET", url, headers=headers)

    # Get the response from GitHub
    response = conn.getresponse()

    # Read and decode the response body
    data = response.read().decode()

    # Close the connection
    conn.close()

    # Convert the JSON string to a Python dictionary and print it
    if response.status == 200:
        user_data = json.loads(data)
        return user_data
    else:
        raise Exception("Failed to retrieve data")

# Create the parser
parser = argparse.ArgumentParser(description="Script to retrieve TacosBot deployment information.")

# Add arguments
parser.add_argument("--repository", type=str, help="The repository to retrieve the deployment information from (i.e. TheTacosBot/tacos-bot)")
parser.add_argument("--project-name", type=str, help="The TacosBot project name to apply (i.e. dir:workflow)")
parser.add_argument("--github-token", type=str, help="GitHub token to make authenticated request")

# Parse the arguments
args = parser.parse_args()

# Define the repository and environment
repository = args.repository
environment = args.project_name

deployments = make_github_request(f"/repos/{repository}/deployments?environment={environment}", args.github_token)


first_deployment_without_success_status = None
for deployment in deployments:
    deployment_status = make_github_request(deployment['statuses_url'], args.github_token)

    # A deployment has an array of statuses, we need to check if any of them are successful
    # We do not want to return successful deployments as they have already been applied
    deployment_has_success_status = False
    for status in deployment_status:
        assert 'state' in status, 'State not found in deployment status'
        if status['state'] == 'success':
            deployment_has_success_status = True
            break
    
    if not deployment_has_success_status:
        first_deployment_without_success_status = deployment
        break

if first_deployment_without_success_status == None:
    raise Exception("Could not find any deployments that have not already been applied")

assert 'payload' in first_deployment_without_success_status, 'Payload not found in deployment'

deployment_info = first_deployment_without_success_status['payload']

if 'GITHUB_OUTPUT' in os.environ:
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f'sha={deployment_info.get("sha")}', file=fh)
        print(f'pr_number={deployment_info.get("pr_number")}', file=fh)
        print(f'project_name={deployment_info.get("project_name")}', file=fh)

        for key, value in deployment_info.get('project').items():
            print(f'{key}={value}', file=fh)
else:
    print(json.dumps(deployment_info, indent=4))
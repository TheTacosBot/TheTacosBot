import subprocess
import json
import os
import argparse
import http.client

def retrieve_deployment_information(repository, environment, github_token):
    # Create a connection to the GitHub API server
    conn = http.client.HTTPSConnection("api.github.com")

    # GitHub personal access token for authentication
    
    # Prepare headers with authorization
    headers = {
        'User-Agent': 'Python http.client',
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Resource URL (for example, fetching user data for a specific username)
    resource = f"/{repository}/deployments?environment={environment}"

    # Send a GET request
    conn.request("GET", resource, headers=headers)

    # Get the response from GitHub
    response = conn.getresponse()

    # Read and decode the response body
    data = response.read().decode()

    # Close the connection
    conn.close()

    # Print the response status and reason
    print(f"Response Status: {response.status}")
    print(f"Response Reason: {response.reason}")

    # Convert the JSON string to a Python dictionary and print it
    if response.status == 200:
        user_data = json.loads(data)
        print(json.dumps(user_data, indent=4))
    else:
        print("Failed to retrieve data")

# Create the parser
parser = argparse.ArgumentParser(description="Script to retrieve TacosBot deployment information.")

# Add arguments
parser.add_argument("--repository", type=str, help="The repository to retrieve the deployment information from (i.e. TheTacosBot/tacos-bot)")
parser.add_argument("--project_name", type=str, help="The TacosBot project name to apply (i.e. dir:workflow)")
parser.add_argument("--github-token", type=str, help="GitHub token to make authenticated request")

# Parse the arguments
args = parser.parse_args()

# Define the repository and environment
repository = args.repository
environment = args.project_name

retrieve_deployment_information(repository, environment, args.github_token)
exit(1)




if deployment:
    deployment_id = deployment.get('id')
    deployment_info = deployment.get('payload')
    
    print(deployment_info)
    exit(1)
    # Extract fields from the payload
    sha = deployment_info.get('sha')
    pr_number = deployment_info.get('pr_number')
    project_name = deployment_info.get('project_name')
    directory = deployment_info.get('project', {}).get('dir')
    workflow = deployment_info.get('project', {}).get('workflow')
    plan_path = deployment_info.get('project', {}).get('plan_path')
    
    # Set outputs for other steps
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f'{name}={value}', file=fh)
    os.system(f"echo 'deployment_id={deployment_id}' >> $GITHUB_ENV")
    os.system(f"echo 'sha={sha}' >> $GITHUB_ENV")
    os.system(f"echo 'pr_number={pr_number}' >> $GITHUB_ENV")
    os.system(f"echo 'project_name={project_name}' >> $GITHUB_ENV")
    os.system(f"echo 'directory={directory}' >> $GITHUB_ENV")
    os.system(f"echo 'workflow={workflow}' >> $GITHUB_ENV")
    os.system(f"echo 'plan_path={plan_path}' >> $GITHUB_ENV")
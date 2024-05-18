## Introduction

TheTacosBot is a GitHub Action based automation tool designed to manage Terraform operations directly within GitHub. Inspired by Atlantis, it allows teams to orchestrate Terraform workflows using GitHub comments and pull request events, streamlining infrastructure as code (IaC) operations without leaving GitHub.

### Features

* Integrated with GitHub Actions: Runs entirely within your GitHub repositories.
* No External Dependencies: Operates with zero dependencies on external services.
* Customizable Workflows: Easily tailor Terraform workflows to suit your team's needs.
* Secure: Executes within the security perimeter of your GitHub environment.

### Getting Started

#### Step 1: Configure GitHub Action

Add the following GitHub Action workflow file to your repository under `.github/workflows/tacosbot.yml`:

```yaml
name: TacosBot

permissions:
  contents: write # Needed to create repository dispatch event
  pull-requests: read
  actions: write
  deployments: write
  statuses: write
  issues: read

on:
  pull_request:
    types: [opened, synchronize, edited, closed]
  issue_comment:
    types: [created]

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          sparse-checkout: |
            ${{ env.config_file }}
          sparse-checkout-cone-mode: false
      - name: Run TacoBot
        uses: TheTacosBot/orchestrator@main
        with:
          config_file: .tacosbot.yaml # You can customize this name.
          github_token: ${{ github.token }}
```

#### Step 2: Create Configuration File

Create a .tacosbot.yaml in the root of your repository with the following content to define the projects and workflows:

```yaml
projects:
  - dir: terraform*
    workflow: tf
```

#### Step 3: Set Up Workflows

Define workflows for handling Terraform plans and applies. For example, add two workflow files:

* `workflow_name_plan.yml` for planning
* `workflow_name_apply.yml` for applying changes

Checkout the [example](examples/) directory for example workflow files.

### Usage

Once set up, TheTacosBot will listen to pull request and issue comment events:

* Pull Requests: Automatically triggers specified workflows when changes are detected in the configured directories.
* Comments: Trigger specific commands by commenting on pull requests:
    * Plan: tacosbot plan --project your_project_name
    * Apply: tacosbot apply --project your_project_name
    * Unlock: tacosbot unlock --project your_project_name

### FAQ
<details>
    <summary>
      How do I customize workflow triggers?
    </summary>
      Edit the on: section of your .github/workflows/tacobot.yml file to trigger workflows based on different GitHub events such as pushes, merges, or manual dispatches.
</details>

<details>
    <summary>
    What if my Terraform configurations are in multiple directories?
    </summary>
    You can specify multiple project entries in .tacosbot.yaml, each with its own directory and workflow.
</details>

<details>
    <summary>
      Can TheTacosBot handle multiple environments like staging and production?
    </summary>
      Yes, you can configure multiple workflows within .tacosbot.yaml to handle different environments.
</details>

### License

TheTacosBot is released under the Prosperity License, a permissive license that allows many uses but requires commercial users to purchase a license. For full license details, see the LICENSE file in the repository.

### Contribution Guidelines

We welcome contributions from the community! If you'd like to contribute:

* Fork the repository.
* Create a new branch for your feature or fix.
* Develop your feature or fix.
* Write appropriate tests for your feature.
* Ensure your code meets the existing style guidelines.
* Submit a pull request against the main branch.

Please ensure your code adheres to best practices and consider performance implications.

### Support

If you encounter issues or have suggestions, please open an issue on the GitHub repository. Our team monitors these issues and will respond as quickly as possible.
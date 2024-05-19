Feature: TacosBot can operate in drift detection mode

	Background:
		Given a configuration file at features/.tacosbot.yaml

	Scenario: TacosBot can detect drift in a repository
		Given drift detection is enabled
		When a pull request is opened
		Then TacosBot triggers jobs
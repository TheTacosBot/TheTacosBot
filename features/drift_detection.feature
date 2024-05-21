Feature: TacosBot can operate in drift detection mode

	Scenario: TacosBot can detect drift in a repository
		Given drift detection is enabled
		When a pull request is opened
		Then TacosBot triggers jobs
# Continuous Integration

Source: https://docs.fontawesome.com/web/dig-deeper/continuous-integration

## The Problem

Repeated package pulls during test suite runs consume significant bandwidth. Every time you push code and your test suite runs, it will pull your packages for each test run.

## The Solution

Implement caching strategies. Once you set up caching, it will only pull packages when something in the package (like a version) changes.

## Supported CI Platforms

- CircleCI
- GitHub Actions
- Travis CI
- GitLab
- Bamboo (Atlassian)
- Jenkins (requires custom implementation)
- Bitbucket Pipelines

Each platform has its own caching documentation for setup.

## Troubleshooting Guidance

1. **Version Consistency**: Verify that `@fortawesome/fontawesome-common-types` and `@fortawesome/fontawesome-svg-core` match other Font Awesome package versions
2. **Package Optimization**: Replace the comprehensive `@fortawesome/fontawesome-pro` package with individual style packages combined with `@fortawesome/fontawesome-svg-core` to reduce download sizes
3. **Version Requirements**: Recommendations assume v6 usage; v5 users should upgrade

# CI and Required Checks

Issue link: #45

Required checks for merge:
- `lint-and-tests`
- `migration-sql-smoke`
- `windows-packaging-smoke`

These checks are defined in `.github/workflows/ci.yml` and run on pull requests and pushes to `main`.
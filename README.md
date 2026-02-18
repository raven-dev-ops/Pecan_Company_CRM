# Pecan Company CRM Planning Assets

This repository currently contains planning and GitHub issue bootstrap assets for the Python + Azure + Legacy Access implementation.

## Files
- `Pecan_POS_Azure_Access_Issues.md`: Updated master requirements/issues document.
- `issues.json`: GitHub labels + issue definitions for bulk issue creation.
- `scripts/create_issues.py`: Script to create labels and issues via GitHub CLI.

## Create GitHub Issues
1. Install GitHub CLI (`gh`) and authenticate:
   ```bash
   gh auth login
   ```
2. Set repository:
   ```bash
   gh repo set-default OWNER/REPO
   ```
3. Run:
   ```bash
   python scripts/create_issues.py issues.json
   ```

## Note
The issue creation script depends on `gh`. If it is not installed in your environment, issue creation must be run on a machine with GitHub CLI available.

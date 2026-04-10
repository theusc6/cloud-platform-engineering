#!/usr/bin/env python3

"""GitHub Enterprise Backup Tool using GitHub CLI.

This script provides functionality to backup all repositories from all organizations
in a GitHub Enterprise instance. It uses mirror cloning for initial backups and
fetch operations for updates to existing backups.

The script handles:
- Authentication via GitHub CLI
- Concurrent repository processing
- Logging of operations
- Directory structure management
- Error handling and reporting

Example:
    $ gh auth login
    $ python3 ghe_backup.py
"""

# Standard library imports
import json
import logging
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# Third-party imports
# pylint: disable=import-error
from git import Repo, GitCommandError, InvalidGitRepositoryError

class GitHubBackup:
    """A class to handle GitHub Enterprise backup operations using GitHub CLI.

    This class manages the backup process for all repositories across all 
    organizations in a GitHub Enterprise instance. It handles authentication,
    API interactions, and local git operations.

    Attributes:
        github_domain (str): Domain of the GitHub Enterprise instance
        backup_dir (Path): Base directory for backups
        date (str): Current date in YYYYMMDD format
        backup_path (Path): Complete path including date for current backup
        logger (logging.Logger): Configured logger for the backup process
    """

    def __init__(self):
        """Initialize backup configuration and setup logging."""
        self.github_domain = "github.example.com"
        self.backup_dir = Path.cwd() / 'github_backup'
        self.date = datetime.now().strftime('%Y%m%d')
        self.backup_path = self.backup_dir / self.date
        self.logger = self._setup_logging()

    def _setup_logging(self):
        """Configure logging with appropriate format and level.

        Returns:
            logging.Logger: Configured logger instance
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def get_organizations(self):
        """Fetch all organizations using GitHub CLI.

        Returns:
            list: List of organization login names

        Raises:
            subprocess.CalledProcessError: If gh command fails
        """
        result = subprocess.run(
            ['gh', 'api', 'user/orgs', '--hostname', self.github_domain],
            capture_output=True,
            text=True,
            check=True
        )
        return [org['login'] for org in json.loads(result.stdout)]

    def get_repositories(self, org):
        """Fetch all repositories for a given organization using GitHub CLI.

        Args:
            org (str): Organization name to fetch repositories for

        Returns:
            list: List of repository names

        Raises:
            subprocess.CalledProcessError: If gh command fails
        """
        result = subprocess.run(
            ['gh', 'api', f'orgs/{org}/repos', '--hostname', self.github_domain],
            capture_output=True,
            text=True,
            check=True
        )
        return [repo['name'] for repo in json.loads(result.stdout)]

    def backup_repository(self, org, repo):
        """Backup a single repository using git mirror clone or fetch.

        Creates a mirror clone of the repository if it doesn't exist,
        otherwise updates the existing mirror.

        Args:
            org (str): Organization name
            repo (str): Repository name

        Returns:
            bool: True if backup successful, False otherwise
        """
        try:
            repo_path = self.backup_path / org / f"{repo}.git"
            repo_path.parent.mkdir(parents=True, exist_ok=True)

            repo_url = f"https://{self.github_domain}/{org}/{repo}.git"
            if repo_path.exists():
                git_repo = Repo(repo_path)
                git_repo.remotes.origin.fetch()
            else:
                Repo.clone_from(repo_url, repo_path, mirror=True)

            self.logger.info("✅ Successfully backed up %s/%s", org, repo)
            return True
        except (GitCommandError, InvalidGitRepositoryError) as e:
            self.logger.error("❌ Failed to backup %s/%s: %s", org, repo, str(e))
            return False

    def run(self):
        """Execute the backup process for all organizations and repositories.

        This is the main entry point for the backup process. It:
        1. Creates necessary directories
        2. Fetches all organizations
        3. Processes all repositories concurrently
        4. Reports on success/failure

        Raises:
            SystemExit: If backup fails
        """
        if self.backup_path.exists():
            response = input(f"⚠️ Backup directory exists: {self.backup_path}\nContinue? [y/N] ")
            if response.lower() != 'y':
                self.logger.info("❌ Backup aborted")
                sys.exit(0)

        self.backup_path.mkdir(parents=True, exist_ok=True)
        self.logger.info("🔍 Starting backup to: %s", self.backup_path)

        try:
            orgs = self.get_organizations()
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for org in orgs:
                    self.logger.info("📂 Processing organization: %s", org)
                    repos = self.get_repositories(org)
                    for repo in repos:
                        futures.append(
                            executor.submit(self.backup_repository, org, repo)
                        )

                successful = sum(1 for future in as_completed(futures) if future.result())
                total = len(futures)

            self.logger.info("✅ Backup completed: %d/%d repositories backed up",
                             successful, total)

        except subprocess.CalledProcessError as e:
            self.logger.error("❌ Backup failed: %s", str(e))
            sys.exit(1)

if __name__ == "__main__":
    GitHubBackup().run()

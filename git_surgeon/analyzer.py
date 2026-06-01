"""
Core analyzer module for extracting Git repository data.
Uses GitPython to parse commits and generate metrics.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError
from pydantic import BaseModel, Field


class CommitData(BaseModel):
    """Represents a commit from the repository."""
    hash: str
    author: str
    author_email: str
    timestamp: datetime
    message: str
    files_changed: list[str] = Field(default_factory=list)
    additions: int = 0
    deletions: int = 0


class RepositoryAnalyzer:
    """
    Main analyzer class for Git repositories.
    Handles reading commits and filtering by date/author.
    """
    
    def __init__(
        self,
        repo_path: str | Path,
        since: Optional[datetime] = None,
        author: Optional[str] = None,
    ):
        """
        Initialize the analyzer.
        
        Args:
            repo_path: Path to the Git repository
            since: Only analyze commits after this date
            author: Only analyze commits from this author (partial match)
        
        Raises:
            InvalidGitRepositoryError: If repo_path is not a valid Git repository
        """
        self.repo_path = Path(repo_path)
        self.since = since
        self.author_filter = author.lower() if author else None
        
        try:
            self.repo = Repo(self.repo_path)
        except InvalidGitRepositoryError as e:
            raise InvalidGitRepositoryError(
                f"'{self.repo_path}' is not a valid Git repository"
            ) from e
    
    def get_branch_name(self) -> str:
        """Get the current branch name."""
        try:
            return self.repo.active_branch.name
        except TypeError:
            return "detached HEAD"
    
    def get_all_commits(self) -> list[CommitData]:
        """
        Fetch all commits from the repository.
        
        Returns:
            List of CommitData objects, filtered by since date and author if specified
        """
        commits = []
        
        try:
            for commit in self.repo.iter_commits():
                # Filter by date
                commit_datetime = datetime.fromtimestamp(commit.committed_date)
                if self.since and commit_datetime < self.since:
                    break
                
                # Filter by author
                if self.author_filter:
                    if self.author_filter not in commit.author.email.lower():
                        continue
                
                # Extract files changed in this commit
                files = []
                if commit.parents:
                    diffs = commit.parents[0].diff(commit)
                    files = [diff.b_path for diff in diffs if diff.b_path]
                
                commit_data = CommitData(
                    hash=commit.hexsha[:7],
                    author=commit.author.name,
                    author_email=commit.author.email,
                    timestamp=commit_datetime,
                    message=commit.message.split("\n")[0],
                    files_changed=files,
                    additions=commit.stats.total.get("insertions", 0),
                    deletions=commit.stats.total.get("deletions", 0),
                )
                commits.append(commit_data)
        
        except GitCommandError as e:
            raise RuntimeError(f"Error reading Git history: {e}") from e
        
        return commits
    
    def get_total_commits(self) -> int:
        """Get the total number of commits in the analyzed range."""
        return len(self.get_all_commits())
    
    def get_stats_summary(self) -> dict:
        """Get summary statistics about the repository."""
        commits = self.get_all_commits()
        
        if not commits:
            return {
                "total_commits": 0,
                "unique_authors": 0,
                "total_additions": 0,
                "total_deletions": 0,
                "first_commit": None,
                "last_commit": None,
            }
        
        unique_authors = set(c.author_email for c in commits)
        total_additions = sum(c.additions for c in commits)
        total_deletions = sum(c.deletions for c in commits)
        
        return {
            "total_commits": len(commits),
            "unique_authors": len(unique_authors),
            "total_additions": total_additions,
            "total_deletions": total_deletions,
            "first_commit": commits[-1].timestamp,
            "last_commit": commits[0].timestamp,
        }

# Enhanced parsing
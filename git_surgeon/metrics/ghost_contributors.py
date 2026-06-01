"""
Ghost contributors analysis module.
Identifies inactive contributors (no commits in last 90 days).
"""

from datetime import datetime, timedelta
from collections import defaultdict
from git_surgeon.analyzer import CommitData


class GhostContributors:
    """Identifies contributors who have gone inactive."""
    
    INACTIVE_DAYS_THRESHOLD = 90
    
    def __init__(self, commits: list[CommitData]):
        """
        Initialize the analyzer.
        
        Args:
            commits: List of commit data to analyze
        """
        self.commits = sorted(commits, key=lambda c: c.timestamp, reverse=True)
    
    def get_inactive_authors(self) -> list[dict]:
        """
        Get authors with no commits in the last 90 days.
        
        Returns:
            List of dicts with author info and inactivity duration
        """
        if not self.commits:
            return []
        
        # Get the most recent commit timestamp as reference
        reference_date = self.commits[0].timestamp
        cutoff_date = reference_date - timedelta(days=self.INACTIVE_DAYS_THRESHOLD)
        
        # Group commits by author
        author_commits: dict[str, list[CommitData]] = defaultdict(list)
        for commit in self.commits:
            author_commits[commit.author_email].append(commit)
        
        # Find inactive authors
        inactive = []
        for author_email, author_commits_list in author_commits.items():
            # Get the most recent commit for this author
            last_commit = max(author_commits_list, key=lambda c: c.timestamp)
            
            # If last commit is before cutoff, author is inactive
            if last_commit.timestamp < cutoff_date:
                days_inactive = (reference_date - last_commit.timestamp).days
                
                inactive.append({
                    "email": author_email,
                    "commit_count": len(author_commits_list),
                    "last_commit": last_commit.timestamp,
                    "days_inactive": days_inactive,
                    "days_inactive_text": self._format_days(days_inactive),
                })
        
        # Sort by most recent inactivity
        inactive.sort(key=lambda x: x["last_commit"], reverse=True)
        return inactive
    
    @staticmethod
    def _format_days(days: int) -> str:
        """
        Format days as readable text.
        
        Args:
            days: Number of days
        
        Returns:
            Formatted string (e.g., "3 meses atrás")
        """
        if days < 1:
            return "hoje"
        elif days < 7:
            return f"{days} dias atrás"
        elif days < 30:
            weeks = days // 7
            return f"{weeks} semana{'s' if weeks > 1 else ''} atrás"
        elif days < 365:
            months = days // 30
            return f"{months} mês{'es' if months > 1 else ''} atrás"
        else:
            years = days // 365
            return f"{years} ano{'s' if years > 1 else ''} atrás"
    
    def get_ghost_score(self) -> float:
        """
        Calculate "ghost score" - measure of project health due to contributor churn.
        Higher score indicates more contributors have gone inactive.
        
        Returns:
            Score between 0-100
        """
        if not self.commits:
            return 0.0
        
        # Get unique authors
        unique_authors = len(set(c.author_email for c in self.commits))
        
        if unique_authors == 0:
            return 0.0
        
        # Count inactive authors
        inactive = self.get_inactive_authors()
        
        # Calculate percentage of authors who are inactive
        inactive_percentage = (len(inactive) / unique_authors) * 100
        
        return min(100, inactive_percentage)

"""
Commits by hour analysis module.
Analyzes when commits are made throughout the day.
"""

from collections import defaultdict
from git_surgeon.analyzer import CommitData


class CommitsByHour:
    """Analyzes commit distribution across hours of the day."""
    
    def __init__(self, commits: list[CommitData]):
        """
        Initialize the analyzer.
        
        Args:
            commits: List of commit data to analyze
        """
        self.commits = commits
    
    def get_hourly_distribution(self) -> dict[int, int]:
        """
        Get number of commits for each hour of the day.
        
        Returns:
            Dictionary mapping hour (0-23) to commit count
        """
        distribution = defaultdict(int)
        
        for commit in self.commits:
            hour = commit.timestamp.hour
            distribution[hour] += 1
        
        # Ensure all 24 hours are represented
        return {hour: distribution.get(hour, 0) for hour in range(24)}
    
    def get_peak_hour(self) -> int:
        """
        Get the hour with most commits.
        
        Returns:
            Hour number (0-23) with maximum commits
        """
        distribution = self.get_hourly_distribution()
        return max(range(24), key=lambda h: distribution[h])
    
    def get_productivity_score(self) -> float:
        """
        Calculate productivity score based on distribution evenness.
        Higher score means more uniform distribution (better work-life balance).
        Lower score means concentrated peak (potential burnout indicator).
        
        Returns:
            Score between 0 and 100
        """
        distribution = self.get_hourly_distribution()
        values = list(distribution.values())
        
        if not values or sum(values) == 0:
            return 0.0
        
        avg = sum(values) / len(values)
        max_val = max(values)
        
        if max_val == 0:
            return 100.0
        
        # Measure how close to ideal (uniform) distribution
        unevenness = (max_val - avg) / max_val if max_val > 0 else 0
        score = max(0, 100 - (unevenness * 100))
        
        return score

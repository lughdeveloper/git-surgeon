"""
Velocity analysis module.
Compares commit activity over time periods to detect project momentum.
"""

from datetime import datetime, timedelta
from git_surgeon.analyzer import CommitData


class Velocity:
    """Analyzes project momentum by comparing commit frequency."""
    
    def __init__(self, commits: list[CommitData]):
        """
        Initialize the analyzer.
        
        Args:
            commits: List of commit data to analyze (sorted by timestamp)
        """
        self.commits = sorted(commits, key=lambda c: c.timestamp)
    
    def get_velocity_comparison(self) -> dict:
        """
        Compare commits from last 30 days vs previous 30 days.
        
        Returns:
            Dictionary with velocity metrics
        """
        if not self.commits:
            return {
                "current_30_days": 0,
                "previous_30_days": 0,
                "change_percentage": 0.0,
                "trend": "stable",
            }
        
        # Get reference date (most recent commit)
        reference_date = self.commits[-1].timestamp
        
        # Define time windows
        current_start = reference_date - timedelta(days=30)
        previous_start = current_start - timedelta(days=30)
        previous_end = current_start
        
        # Count commits in each window
        current_commits = [
            c for c in self.commits
            if c.timestamp >= current_start
        ]
        
        previous_commits = [
            c for c in self.commits
            if previous_start <= c.timestamp < previous_end
        ]
        
        current_count = len(current_commits)
        previous_count = len(previous_commits)
        
        # Calculate percentage change
        if previous_count == 0:
            change_percentage = 100.0 if current_count > 0 else 0.0
        else:
            change_percentage = ((current_count - previous_count) / previous_count) * 100
        
        # Determine trend
        if change_percentage > 10:
            trend = "up"
        elif change_percentage < -10:
            trend = "down"
        else:
            trend = "stable"
        
        return {
            "current_30_days": current_count,
            "previous_30_days": previous_count,
            "change_percentage": change_percentage,
            "trend": trend,
        }
    
    def get_velocity_score(self) -> float:
        """
        Calculate velocity score (0-100).
        Score indicates if the project maintains or improves its pace.
        
        Returns:
            Velocity score
        """
        velocity = self.get_velocity_comparison()
        change = velocity["change_percentage"]
        
        # Ideal is slight growth (5-15%), penalty for stagnation or decline
        if -10 <= change <= 20:
            # Good range
            score = 75 + (change / 4)  # Up to 85 with growth
        elif change > 20:
            # Good but might be unsustainable
            score = 85
        elif change > -30:
            # Slight decline but manageable
            score = 50 + ((change + 30) / 3)
        else:
            # Significant decline
            score = max(20, 50 + ((change + 30) / 3))
        
        return max(0, min(100, score))
    
    def get_commits_by_month(self, months: int = 6) -> dict[str, int]:
        """
        Get commit counts by month for trend visualization.
        
        Args:
            months: Number of months to analyze (default: 6)
        
        Returns:
            Dictionary mapping month to commit count
        """
        monthly_counts: dict[str, int] = {}
        
        if not self.commits:
            return monthly_counts
        
        reference_date = self.commits[-1].timestamp
        
        for i in range(months, 0, -1):
            month_date = reference_date - timedelta(days=30 * i)
            month_key = month_date.strftime("%Y-%m")
            
            month_start = month_date.replace(day=1)
            if i == 1:
                month_end = reference_date
            else:
                month_end = (month_date.replace(day=1) + timedelta(days=32)).replace(day=1)
            
            month_commits = [
                c for c in self.commits
                if month_start <= c.timestamp < month_end
            ]
            
            monthly_counts[month_key] = len(month_commits)
        
        return monthly_counts

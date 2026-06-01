"""
Volatile files analysis module.
Identifies files that change frequently (potential problem areas).
"""

from collections import Counter
from git_surgeon.analyzer import CommitData


class VolatileFiles:
    """Analyzes which files change most frequently."""
    
    def __init__(self, commits: list[CommitData], top_limit: int = 10):
        """
        Initialize the analyzer.
        
        Args:
            commits: List of commit data to analyze
            top_limit: Maximum number of files to track
        """
        self.commits = commits
        self.top_limit = top_limit
    
    def get_file_change_counts(self) -> dict[str, int]:
        """
        Count how many times each file appears in commits.
        
        Returns:
            Dictionary mapping file path to commit count
        """
        file_counter: Counter[str] = Counter()
        
        for commit in self.commits:
            for filepath in commit.files_changed:
                file_counter[filepath] += 1
        
        return dict(file_counter)
    
    def get_top_files(self) -> list[tuple[str, int]]:
        """
        Get the most frequently changed files.
        
        Returns:
            List of tuples: (filepath, change_count)
        """
        file_counts = self.get_file_change_counts()
        
        # Sort by count (descending)
        sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_files[:self.top_limit]
    
    def get_volatility_index(self) -> float:
        """
        Calculate volatility index (0-100).
        High index means few files are changed very frequently (concentration).
        Low index means changes are distributed across many files.
        
        Returns:
            Volatility score
        """
        file_counts = self.get_file_change_counts()
        
        if not file_counts:
            return 0.0
        
        if len(file_counts) <= 1:
            return 100.0
        
        # Calculate concentration: if top files account for large % of changes
        total_changes = sum(file_counts.values())
        top_10_changes = sum(count for _, count in self.get_top_files())
        
        # Normalize to 0-100: higher means more concentrated volatility
        concentration = (top_10_changes / total_changes * 100) if total_changes > 0 else 0
        
        return min(100, concentration)

# Optimize file volatility calculation
"""
Co-change analysis module.
Identifies files that frequently change together (implicit coupling).
"""

from collections import Counter, defaultdict
from git_surgeon.analyzer import CommitData


class CochangeAnalysis:
    """Analyzes which files change together frequently."""
    
    def __init__(self, commits: list[CommitData], top_limit: int = 10):
        """
        Initialize the analyzer.
        
        Args:
            commits: List of commit data to analyze
            top_limit: Maximum number of pairs to track
        """
        self.commits = commits
        self.top_limit = top_limit
    
    def get_file_pairs(self) -> list[tuple[str, str, int]]:
        """
        Find all pairs of files that change together.
        
        Returns:
            List of tuples: (file1, file2, frequency)
        """
        pair_counter: Counter[tuple[str, str]] = Counter()
        
        for commit in self.commits:
            files = sorted(set(commit.files_changed))
            
            # Create pairs from all files in this commit
            if len(files) >= 2:
                for i, file1 in enumerate(files):
                    for file2 in files[i + 1:]:
                        # Normalize pair order for consistent counting
                        pair = tuple(sorted([file1, file2]))
                        pair_counter[pair] += 1
        
        # Convert to list and filter pairs that occurred at least twice
        pairs = [
            (file1, file2, count)
            for (file1, file2), count in pair_counter.items()
            if count >= 2
        ]
        
        return pairs
    
    def get_top_pairs(self) -> list[tuple[str, str, int]]:
        """
        Get the top co-changing file pairs.
        
        Returns:
            List of top pairs sorted by frequency
        """
        pairs = self.get_file_pairs()
        # Sort by frequency (descending)
        sorted_pairs = sorted(pairs, key=lambda x: x[2], reverse=True)
        return sorted_pairs[:self.top_limit]
    
    def get_coupling_index(self) -> float:
        """
        Calculate overall coupling index (0-100).
        High coupling means many files change together (potential design issues).
        
        Returns:
            Coupling score
        """
        if not self.commits:
            return 0.0
        
        total_files_changed = sum(
            len(set(commit.files_changed)) for commit in self.commits
        )
        
        pairs = self.get_file_pairs()
        if not pairs:
            return 0.0
        
        # Average frequency of co-changes normalized to total files
        avg_pair_frequency = sum(f for _, _, f in pairs) / len(pairs)
        
        # Normalize to 0-100 scale
        coupling = min(100, (avg_pair_frequency / (total_files_changed / len(self.commits))) * 100)
        return coupling

# Improved cochange detection
# Improved co-change frequency calculation
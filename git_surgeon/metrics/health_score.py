"""
Health score calculation module.
Combines all metrics into a single health score (0-100).
"""


class HealthScore:
    """Calculates overall repository health based on all metrics."""
    
    def __init__(
        self,
        commits_by_hour: dict[int, int],
        cochange_pairs: list[tuple[str, str, int]],
        ghost_contributors: list[dict],
        volatile_files: list[tuple[str, int]],
        velocity: dict,
    ):
        """
        Initialize with metric results.
        
        Args:
            commits_by_hour: Distribution of commits by hour
            cochange_pairs: List of file pairs with co-change frequency
            ghost_contributors: List of inactive contributors
            volatile_files: List of frequently changed files
            velocity: Velocity metrics
        """
        self.commits_by_hour = commits_by_hour
        self.cochange_pairs = cochange_pairs
        self.ghost_contributors = ghost_contributors
        self.volatile_files = volatile_files
        self.velocity = velocity
    
    def calculate_score(self) -> tuple[int, str]:
        """
        Calculate overall health score and label.
        
        Returns:
            Tuple of (score: 0-100, label: health category)
        """
        score = 100  # Start with perfect score
        
        # Factor 1: Developer productivity/work-life balance (20 points)
        score -= self._score_work_life_balance()
        
        # Factor 2: Code coupling (25 points)
        score -= self._score_code_coupling()
        
        # Factor 3: Team continuity (20 points)
        score -= self._score_team_continuity()
        
        # Factor 4: Code stability (20 points)
        score -= self._score_code_stability()
        
        # Factor 5: Project momentum (15 points)
        score -= self._score_project_momentum()
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        # Determine label
        if score >= 80:
            label = "Excelente"
        elif score >= 60:
            label = "Saudável"
        elif score >= 40:
            label = "Regular"
        else:
            label = "Crítico"
        
        return score, label
    
    def _score_work_life_balance(self) -> int:
        """
        Score based on distribution of commits across hours.
        Perfect: commits distributed evenly
        Poor: all commits at odd hours (burnout indicator)
        
        Returns:
            Points to deduct (0-20)
        """
        if not self.commits_by_hour:
            return 0
        
        values = list(self.commits_by_hour.values())
        if not values or sum(values) == 0:
            return 0
        
        # Calculate evenness
        avg = sum(values) / len(values)
        max_val = max(values)
        
        if max_val == 0:
            return 0
        
        # Unevenness factor
        unevenness = (max_val - avg) / max_val
        
        # Deduct up to 20 points based on unevenness
        return int(unevenness * 20)
    
    def _score_code_coupling(self) -> int:
        """
        Score based on file co-change patterns.
        High coupling (many files changing together) indicates design issues.
        
        Returns:
            Points to deduct (0-25)
        """
        if not self.cochange_pairs:
            return 0
        
        # High frequency co-changes are bad
        total_cochange_frequency = sum(f for _, _, f in self.cochange_pairs[:10])
        average_cochange = total_cochange_frequency / len(self.cochange_pairs[:10])
        
        # Normalize to 0-25 scale
        # Threshold: more than 20 co-changes per pair is concerning
        if average_cochange > 50:
            return 25
        elif average_cochange > 20:
            return 15
        elif average_cochange > 10:
            return 8
        else:
            return 0
    
    def _score_team_continuity(self) -> int:
        """
        Score based on inactive contributors.
        Too many inactive contributors indicates project is losing momentum.
        
        Returns:
            Points to deduct (0-20)
        """
        if not self.ghost_contributors:
            return 0
        
        # Deduct based on number of inactive contributors
        num_ghosts = len(self.ghost_contributors)
        
        if num_ghosts <= 1:
            return 0
        elif num_ghosts <= 3:
            return 5
        elif num_ghosts <= 5:
            return 10
        elif num_ghosts <= 8:
            return 15
        else:
            return 20
    
    def _score_code_stability(self) -> int:
        """
        Score based on volatile files.
        Files that change too frequently indicate instability.
        
        Returns:
            Points to deduct (0-20)
        """
        if not self.volatile_files:
            return 0
        
        # Get top file change count
        top_file_changes = self.volatile_files[0][1] if self.volatile_files else 0
        
        # Normalize: if one file has more than 20% of all changes, it's concerning
        total_file_changes = sum(count for _, count in self.volatile_files)
        
        if total_file_changes == 0:
            return 0
        
        top_percentage = (top_file_changes / total_file_changes) * 100
        
        if top_percentage > 30:
            return 20
        elif top_percentage > 20:
            return 15
        elif top_percentage > 10:
            return 8
        else:
            return 0
    
    def _score_project_momentum(self) -> int:
        """
        Score based on velocity trend.
        Declining velocity is a concern.
        
        Returns:
            Points to deduct (0-15)
        """
        change = self.velocity.get("change_percentage", 0)
        
        # Ideal: slight growth (5-15%)
        if -10 <= change <= 20:
            return 0
        elif -30 <= change <= -10:
            return 8
        elif change < -30:
            return 15
        elif change > 20 and change <= 50:
            return 3  # Small deduction for excessive growth (unsustainable)
        else:
            return 0

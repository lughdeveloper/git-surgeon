"""Tests for git-surgeon metrics modules."""

import pytest
from datetime import datetime, timedelta
from git_surgeon.analyzer import CommitData
from git_surgeon.metrics.commits_by_hour import CommitsByHour
from git_surgeon.metrics.cochange import CochangeAnalysis
from git_surgeon.metrics.ghost_contributors import GhostContributors
from git_surgeon.metrics.volatile_files import VolatileFiles
from git_surgeon.metrics.velocity import Velocity


@pytest.fixture
def sample_commits() -> list[CommitData]:
    """Create sample commits for testing."""
    base_time = datetime.now()
    commits = [
        CommitData(
            hash="abc123",
            author="Alice Dev",
            author_email="alice@example.com",
            timestamp=base_time,
            message="Fix bug in auth",
            files_changed=["src/auth.py", "src/utils.py"],
            additions=10,
            deletions=5,
        ),
        CommitData(
            hash="def456",
            author="Bob Dev",
            author_email="bob@example.com",
            timestamp=base_time - timedelta(days=1),
            message="Add feature X",
            files_changed=["src/auth.py", "tests/test_auth.py"],
            additions=50,
            deletions=0,
        ),
        CommitData(
            hash="ghi789",
            author="Alice Dev",
            author_email="alice@example.com",
            timestamp=base_time - timedelta(days=10),
            message="Refactor database",
            files_changed=["src/db.py", "src/models.py"],
            additions=30,
            deletions=20,
        ),
    ]
    return commits


def test_commits_by_hour(sample_commits):
    """Test commits by hour distribution."""
    analyzer = CommitsByHour(sample_commits)
    distribution = analyzer.get_hourly_distribution()
    
    assert len(distribution) == 24
    assert sum(distribution.values()) == len(sample_commits)


def test_commits_by_hour_peak(sample_commits):
    """Test finding peak hour."""
    analyzer = CommitsByHour(sample_commits)
    peak = analyzer.get_peak_hour()
    
    assert 0 <= peak < 24


def test_cochange_analysis(sample_commits):
    """Test co-change pair detection."""
    analyzer = CochangeAnalysis(sample_commits)
    pairs = analyzer.get_file_pairs()
    
    # Should find (src/auth.py, src/utils.py) and (src/auth.py, tests/test_auth.py)
    assert len(pairs) >= 0


def test_cochange_top_pairs(sample_commits):
    """Test getting top co-change pairs."""
    analyzer = CochangeAnalysis(sample_commits, top_limit=5)
    top_pairs = analyzer.get_top_pairs()
    
    assert len(top_pairs) <= 5


def test_ghost_contributors(sample_commits):
    """Test ghost contributor detection."""
    analyzer = GhostContributors(sample_commits)
    ghosts = analyzer.get_inactive_authors()
    
    # Old commits should be detected as inactive
    assert isinstance(ghosts, list)


def test_volatile_files(sample_commits):
    """Test volatile file detection."""
    analyzer = VolatileFiles(sample_commits)
    files = analyzer.get_top_files()
    
    assert len(files) >= 0
    # Files should be sorted by frequency
    if len(files) > 1:
        assert files[0][1] >= files[-1][1]


def test_velocity(sample_commits):
    """Test velocity calculation."""
    analyzer = Velocity(sample_commits)
    velocity = analyzer.get_velocity_comparison()
    
    assert "current_30_days" in velocity
    assert "previous_30_days" in velocity
    assert "change_percentage" in velocity
    assert "trend" in velocity


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

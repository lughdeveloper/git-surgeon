"""
CLI entry point for git-surgeon.
Provides command-line interface using Typer.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from git.exc import InvalidGitRepositoryError

from git_surgeon import __version__
from git_surgeon.analyzer import RepositoryAnalyzer
from git_surgeon.reporter import Reporter

app = typer.Typer(
    help="🔪 git-surgeon: Analyze Git repositories and generate health reports",
    no_args_is_help=True,
)


@app.command()
def analyze(
    repo_path: str = typer.Argument(
        ".",
        help="Path to the Git repository",
        metavar="<repo-path>",
    ),
    since: Optional[str] = typer.Option(
        None,
        "--since",
        help="Analyze commits since this date (YYYY-MM-DD)",
        metavar="DATE",
    ),
    author: Optional[str] = typer.Option(
        None,
        "--author",
        help="Filter commits by author (partial match on email)",
        metavar="AUTHOR",
    ),
    top: int = typer.Option(
        10,
        "--top",
        help="Number of results to show in rankings (default: 10)",
        min=1,
        max=100,
    ),
    export: Optional[str] = typer.Option(
        None,
        "--export",
        help="Export report to HTML file",
        metavar="FILE",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
) -> None:
    """
    Analyze a Git repository and generate a health report.
    
    Examples:
    
        git-surgeon analyze ./my-project
        
        git-surgeon analyze ./my-project --since 2024-01-01
        
        git-surgeon analyze ./my-project --author "john@example.com"
        
        git-surgeon analyze ./my-project --export report.html --top 20
    """
    try:
        # Parse since date if provided
        since_date = None
        if since:
            try:
                since_date = datetime.strptime(since, "%Y-%m-%d")
            except ValueError:
                typer.echo(
                    f"❌ Invalid date format: {since}. Use YYYY-MM-DD",
                    err=True,
                )
                raise typer.Exit(1)
        
        # Initialize analyzer
        typer.echo(f"🔍 Analyzing repository: {repo_path}", err=False)
        analyzer = RepositoryAnalyzer(repo_path, since=since_date, author=author)
        
        # Create reporter and generate report
        reporter = Reporter(analyzer, top_limit=top, verbose=verbose)
        report = reporter.generate_report()
        
        # Display report in terminal
        reporter.display_report(report)
        
        # Export to HTML if requested
        if export:
            export_path = Path(export)
            reporter.export_html(report, export_path)
            typer.echo(f"\n✅ Report exported to: {export_path.absolute()}")
    
    except InvalidGitRepositoryError as e:
        typer.echo(f"❌ {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    typer.echo(f"git-surgeon version {__version__}")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()

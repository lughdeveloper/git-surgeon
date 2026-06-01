"""
Reporter module for rendering analysis results.
Uses Rich for terminal visualization and supports HTML export.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from git_surgeon.analyzer import RepositoryAnalyzer
from git_surgeon.metrics.commits_by_hour import CommitsByHour
from git_surgeon.metrics.cochange import CochangeAnalysis
from git_surgeon.metrics.ghost_contributors import GhostContributors
from git_surgeon.metrics.volatile_files import VolatileFiles
from git_surgeon.metrics.velocity import Velocity
from git_surgeon.metrics.health_score import HealthScore


class Report:
    """Container for analysis results."""
    
    def __init__(self):
        self.timestamp = datetime.now()
        self.repo_info: dict[str, Any] = {}
        self.commits_by_hour: dict[int, int] = {}
        self.peak_hour: int = 0
        self.cochange_pairs: list[tuple[str, str, int]] = []
        self.ghost_contributors: list[dict[str, Any]] = []
        self.volatile_files: list[tuple[str, int]] = []
        self.velocity: dict[str, Any] = {}
        self.health_score: int = 0
        self.health_label: str = ""
        self.analysis_time: float = 0.0


class Reporter:
    """Generates and displays repository health reports."""
    
    def __init__(
        self,
        analyzer: RepositoryAnalyzer,
        top_limit: int = 10,
        verbose: bool = False,
    ):
        self.analyzer = analyzer
        self.top_limit = top_limit
        self.verbose = verbose
        self.console = Console()
    
    def generate_report(self) -> Report:
        """
        Generate a complete health report.
        
        Returns:
            Report object containing all analysis results
        """
        start_time = time.time()
        report = Report()
        
        # Get repository info
        stats = self.analyzer.get_stats_summary()
        report.repo_info = {
            "path": str(self.analyzer.repo_path),
            "branch": self.analyzer.get_branch_name(),
            "total_commits": stats["total_commits"],
            "unique_authors": stats["unique_authors"],
            "total_additions": stats["total_additions"],
            "total_deletions": stats["total_deletions"],
            "first_commit": stats["first_commit"],
            "last_commit": stats["last_commit"],
        }
        
        # Run all metrics
        commits = self.analyzer.get_all_commits()
        
        if commits:
            # Commits by hour
            cbh = CommitsByHour(commits)
            report.commits_by_hour = cbh.get_hourly_distribution()
            report.peak_hour = cbh.get_peak_hour()
            
            # Co-change analysis
            cochange = CochangeAnalysis(commits, top_limit=self.top_limit)
            report.cochange_pairs = cochange.get_top_pairs()
            
            # Ghost contributors
            ghost = GhostContributors(commits)
            report.ghost_contributors = ghost.get_inactive_authors()
            
            # Volatile files
            volatile = VolatileFiles(commits, top_limit=self.top_limit)
            report.volatile_files = volatile.get_top_files()
            
            # Velocity
            velocity = Velocity(commits)
            report.velocity = velocity.get_velocity_comparison()
            
            # Health score
            health = HealthScore(
                report.commits_by_hour,
                report.cochange_pairs,
                report.ghost_contributors,
                report.volatile_files,
                report.velocity,
            )
            report.health_score, report.health_label = health.calculate_score()
        
        report.analysis_time = time.time() - start_time
        return report
    
    def display_report(self, report: Report) -> None:
        """
        Display the report in the terminal using Rich.
        
        Args:
            report: Report object to display
        """
        # Header
        self._display_header(report)
        
        if report.repo_info["total_commits"] == 0:
            self.console.print("\n[red]⚠️  No commits found in this repository[/red]\n")
            return
        
        self.console.print()
        
        # Commits by hour
        self._display_commits_by_hour(report)
        self.console.print()
        
        # Co-change analysis
        self._display_cochange(report)
        self.console.print()
        
        # Ghost contributors
        self._display_ghost_contributors(report)
        self.console.print()
        
        # Volatile files
        self._display_volatile_files(report)
        self.console.print()
        
        # Velocity
        self._display_velocity(report)
        self.console.print()
        
        # Health score
        self._display_health_score(report)
        
        # Footer
        self._display_footer(report)
    
    def _display_header(self, report: Report) -> None:
        """Display header panel with repository info."""
        repo_name = self.analyzer.repo_path.name or "repository"
        branch = report.repo_info["branch"]
        total_commits = report.repo_info["total_commits"]
        
        header_text = f"🔪 git-surgeon · Relatório de Saúde\n"
        header_text += f"Repo: [bold]{repo_name}[/bold]  Branch: [bold]{branch}[/bold]\n"
        header_text += f"Commits analisados: [bold]{total_commits:,}[/bold]"
        
        panel = Panel(
            header_text,
            style="bold cyan",
            expand=False,
            padding=(1, 2),
        )
        self.console.print(panel)
    
    def _display_commits_by_hour(self, report: Report) -> None:
        """Display commits by hour analysis."""
        self.console.print("[bold cyan]📊 Commits por hora do dia[/bold cyan]")
        
        max_commits = max(report.commits_by_hour.values()) if report.commits_by_hour else 1
        peak = report.peak_hour
        
        for hour in range(24):
            count = report.commits_by_hour.get(hour, 0)
            bar_width = 20
            filled = int((count / max_commits) * bar_width) if max_commits > 0 else 0
            bar = "█" * filled + "░" * (bar_width - filled)
            
            # Highlight peak hour
            peak_marker = " ← pico" if hour == peak else ""
            color = "bold yellow" if hour == peak else "default"
            
            self.console.print(
                f"  [dim]{hour:02d}h[/dim] [{color}]{bar}[/{color}]  "
                f"[dim]{count:3d}[/dim]{peak_marker}"
            )
    
    def _display_cochange(self, report: Report) -> None:
        """Display co-change analysis."""
        self.console.print("[bold cyan]🔗 Arquivos com maior acoplamento[/bold cyan]")
        
        if not report.cochange_pairs:
            self.console.print("  [dim]Nenhum padrão de co-change encontrado[/dim]")
            return
        
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Arquivo 1", style="cyan")
        table.add_column("", width=3, justify="center")
        table.add_column("Arquivo 2", style="cyan")
        table.add_column("Frequência", justify="right", style="yellow")
        
        for file1, file2, freq in report.cochange_pairs[:self.top_limit]:
            table.add_row(file1, "↔", file2, str(freq))
        
        self.console.print(table)
    
    def _display_ghost_contributors(self, report: Report) -> None:
        """Display inactive contributors."""
        self.console.print("[bold cyan]👻 Contribuidores fantasmas[/bold cyan]")
        
        if not report.ghost_contributors:
            self.console.print("  [dim]Nenhum contribuidor inativo (90+ dias) encontrado[/dim]")
            return
        
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Email", style="cyan")
        table.add_column("Commits", justify="right", style="yellow")
        table.add_column("Último commit", style="dim")
        
        for contributor in report.ghost_contributors[:self.top_limit]:
            table.add_row(
                contributor["email"],
                str(contributor["commit_count"]),
                contributor["days_inactive_text"],
            )
        
        self.console.print(table)
    
    def _display_volatile_files(self, report: Report) -> None:
        """Display volatile files analysis."""
        self.console.print("[bold cyan]⚡ Arquivos mais voláteis[/bold cyan]")
        
        if not report.volatile_files:
            self.console.print("  [dim]Nenhum arquivo encontrado[/dim]")
            return
        
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Arquivo", style="cyan")
        table.add_column("Commits", justify="right", style="yellow")
        
        for filepath, count in report.volatile_files[:self.top_limit]:
            table.add_row(filepath, str(count))
        
        self.console.print(table)
    
    def _display_velocity(self, report: Report) -> None:
        """Display project velocity."""
        self.console.print("[bold cyan]📈 Velocidade do projeto[/bold cyan]")
        
        current = report.velocity.get("current_30_days", 0)
        previous = report.velocity.get("previous_30_days", 0)
        change = report.velocity.get("change_percentage", 0)
        trend = report.velocity.get("trend", "stable")
        
        trend_emoji = {"up": "↑", "down": "↓", "stable": "→"}[trend]
        color = {"up": "green", "down": "red", "stable": "yellow"}[trend]
        
        self.console.print(f"  Últimos 30 dias: [bold]{current}[/bold] commits")
        self.console.print(f"  30 dias anteriores: [bold]{previous}[/bold] commits")
        self.console.print(
            f"  Variação: [{color}]{change:+.1f}% {trend_emoji}[/{color}]"
        )
    
    def _display_health_score(self, report: Report) -> None:
        """Display overall health score."""
        score = report.health_score
        label = report.health_label
        
        # Color based on score
        if score >= 80:
            color = "bold green"
            emoji = "✅"
        elif score >= 60:
            color = "bold yellow"
            emoji = "⚠️"
        elif score >= 40:
            color = "bold red"
            emoji = "❌"
        else:
            color = "bold bright_red"
            emoji = "🔴"
        
        text = f"Score de saúde: [{color}]{score}/100[/{color}]  ·  {emoji} {label}"
        panel = Panel(text, style=color, expand=False, padding=(1, 2))
        self.console.print(panel)
    
    def _display_footer(self, report: Report) -> None:
        """Display footer with timing info."""
        self.console.print(
            f"[dim]Análise concluída em {report.analysis_time:.2f}s[/dim]"
        )
    
    def export_html(self, report: Report, output_path: Path) -> None:
        """
        Export report to HTML file.
        
        Args:
            report: Report object to export
            output_path: Path to save the HTML file
        """
        html = self._generate_html(report)
        output_path.write_text(html, encoding="utf-8")
    
    def _generate_html(self, report: Report) -> str:
        """Generate HTML representation of the report."""
        repo_name = self.analyzer.repo_path.name or "repository"
        branch = report.repo_info["branch"]
        total_commits = report.repo_info["total_commits"]
        score = report.health_score
        
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>git-surgeon · {repo_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2em;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .info-item {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 4px;
            backdrop-filter: blur(10px);
        }}
        .info-label {{
            opacity: 0.9;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .info-value {{
            font-size: 1.5em;
            font-weight: bold;
            margin-top: 5px;
        }}
        .section {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #667eea;
            margin-top: 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #667eea;
            border-bottom: 2px solid #e0e0e0;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .bar {{
            display: inline-block;
            background: #667eea;
            height: 20px;
            border-radius: 3px;
            min-width: 50px;
        }}
        .score-panel {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            text-align: center;
            margin: 20px 0;
        }}
        .score-value {{
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .score-label {{
            font-size: 1.2em;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        .footer {{
            text-align: center;
            color: #999;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔪 git-surgeon</h1>
        <p>Relatório de Saúde do Repositório</p>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Repositório</div>
                <div class="info-value">{repo_name}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Branch</div>
                <div class="info-value">{branch}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Total de Commits</div>
                <div class="info-value">{total_commits:,}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Autores Únicos</div>
                <div class="info-value">{report.repo_info["unique_authors"]}</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>📊 Commits por Hora do Dia</h2>
        <table>
            <tr>
                <th>Hora</th>
                <th>Commits</th>
                <th>Visualização</th>
            </tr>
"""
        
        max_commits = max(report.commits_by_hour.values()) if report.commits_by_hour else 1
        for hour in range(24):
            count = report.commits_by_hour.get(hour, 0)
            bar_width = int((count / max_commits) * 200) if max_commits > 0 else 0
            html += f"""            <tr>
                <td>{hour:02d}:00</td>
                <td>{count}</td>
                <td><div class="bar" style="width: {bar_width}px;"></div></td>
            </tr>
"""
        
        html += """        </table>
    </div>
    
    <div class="section">
        <h2>🔗 Arquivos com Maior Acoplamento</h2>
        <table>
            <tr>
                <th>Arquivo 1</th>
                <th>Arquivo 2</th>
                <th>Frequência</th>
            </tr>
"""
        
        for file1, file2, freq in report.cochange_pairs[:10]:
            html += f"""            <tr>
                <td>{file1}</td>
                <td>{file2}</td>
                <td>{freq}</td>
            </tr>
"""
        
        html += """        </table>
    </div>
    
    <div class="section">
        <h2>👻 Contribuidores Fantasmas</h2>
        <table>
            <tr>
                <th>Email</th>
                <th>Commits</th>
                <th>Inativo há</th>
            </tr>
"""
        
        for contributor in report.ghost_contributors[:10]:
            html += f"""            <tr>
                <td>{contributor["email"]}</td>
                <td>{contributor["commit_count"]}</td>
                <td>{contributor["days_inactive_text"]}</td>
            </tr>
"""
        
        html += """        </table>
    </div>
    
    <div class="section">
        <h2>⚡ Arquivos Mais Voláteis</h2>
        <table>
            <tr>
                <th>Arquivo</th>
                <th>Commits</th>
            </tr>
"""
        
        for filepath, count in report.volatile_files[:10]:
            html += f"""            <tr>
                <td>{filepath}</td>
                <td>{count}</td>
            </tr>
"""
        
        html += f"""        </table>
    </div>
    
    <div class="section">
        <h2>📈 Velocidade do Projeto</h2>
        <p>
            <strong>Últimos 30 dias:</strong> {report.velocity.get('current_30_days', 0)} commits<br>
            <strong>30 dias anteriores:</strong> {report.velocity.get('previous_30_days', 0)} commits<br>
            <strong>Variação:</strong> {report.velocity.get('change_percentage', 0):+.1f}% {report.velocity.get('trend', 'stable')}
        </p>
    </div>
    
    <div class="score-panel">
        <div class="score-label">Score de Saúde</div>
        <div class="score-value">{score}</div>
        <div class="score-label">{report.health_label}</div>
    </div>
    
    <div class="footer">
        <p>Gerado em {report.timestamp.strftime('%d/%m/%Y %H:%M:%S')} · git-surgeon v1.0</p>
    </div>
</body>
</html>
"""
        return html

# Better HTML export formatting
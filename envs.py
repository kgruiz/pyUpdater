import re
import subprocess
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

console = Console()
targetVersion = "3.13.2"


def GetEnvs() -> list[str]:
    """
    Returns a list of conda environments.

    Returns
    -------
    list of str
        A list of environment names.
    """

    result = subprocess.run(["conda", "env", "list"], stdout=subprocess.PIPE, text=True)

    envs = []

    for line in result.stdout.splitlines():

        if line.startswith("#") or not line.strip():
            continue

        parts = line.split()

        if parts[0] != "base":
            envs.append(parts[0])

    return envs


def GetPythonVersion(env: str) -> str | None:
    """
    Gets the Python version for a given conda environment.

    Parameters
    ----------
    env : str
        The name of the conda environment.

    Returns
    -------
    str or None
        The Python version, or None if not found.
    """

    result = subprocess.run(
        ["conda", "run", "-n", env, "python", "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    m = re.search(r"Python\s+(\S+)", result.stdout + result.stderr)

    return m.group(1) if m else None


def UpgradeEnv(env: str) -> subprocess.CompletedProcess:
    """
    Upgrades the Python version in a given conda environment.

    Parameters
    ----------
    env : str
        The name of the conda environment.

    Returns
    -------
    subprocess.CompletedProcess
        The result of the subprocess run.
    """

    return subprocess.run(
        [
            "conda",
            "install",
            "-n",
            env,
            f"python={targetVersion}",
            "--update-deps",
            "-y",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


if __name__ == "__main__":

    envs = GetEnvs()

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}", justify="left"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        BarColumn(bar_width=None),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
        expand=True,
        console=console,
    ) as progress:

        task = progress.add_task("Upgrading Python in environments", total=len(envs))

        for env in envs:

            current = GetPythonVersion(env)

            if not current:
                console.print(Panel(f"[yellow]{env}: No Python found[/]"))
                progress.advance(task)

                continue

            if current != targetVersion:
                console.print(
                    Panel(
                        f"[blue]{env}[/]: [yellow]{current}[/] → [green]{targetVersion}[/]"
                    )
                )

                result = UpgradeEnv(env)

                if result.returncode == 0:
                    console.print(
                        Panel(
                            f"[blue]{env}[/]: [green]Upgraded successfully to {targetVersion}[/]"
                        )
                    )
                else:
                    console.print(Panel(f"[blue]{env}[/]: [red]Upgrade failed[/]"))
            else:
                console.print(
                    Panel(f"[blue]{env}[/]: Already at [green]{targetVersion}[/]")
                )

            progress.advance(task)

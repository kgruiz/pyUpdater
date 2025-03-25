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


class GetEnvs:
    """
    Retrieves the list of Conda environments.

    Returns
    -------
    list[str]
        A list of environment names.
    """

    def __call__(self) -> list[str]:
        result = subprocess.run(
            ["conda", "env", "list"], stdout=subprocess.PIPE, text=True
        )
        envs = []

        for line in result.stdout.splitlines():

            if line.startswith("#") or not line.strip():
                continue

            parts = line.split()
            if parts[0] != "base":
                envs.append(parts[0])

        return envs


class UpdateEnv:
    """
    Updates all dependencies in a given Conda environment.

    Parameters
    ----------
    env : str
        The name of the Conda environment to update.

    Returns
    -------
    subprocess.CompletedProcess
        The result of the subprocess run.
    """

    def __call__(self, env: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["conda", "update", "--all", "-n", env, "-y"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )


if __name__ == "__main__":

    getEnvs = GetEnvs()
    updateEnv = UpdateEnv()

    envs = getEnvs()

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

        task = progress.add_task(
            "Updating dependencies in environments", total=len(envs)
        )

        for env in envs:

            console.print(Panel(f"[blue]{env}[/]: Updating dependencies"))
            result = updateEnv(env)

            if result.returncode == 0:

                console.print(
                    Panel(
                        f"[blue]{env}[/]: [green]Dependencies updated successfully[/]"
                    )
                )

            else:

                console.print(Panel(f"[blue]{env}[/]: [red]Update failed[/]"))

            progress.advance(task)

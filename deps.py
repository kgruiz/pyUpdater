import json
import subprocess

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
from rich.table import Table

console = Console()


class GetEnvs:
    def __call__(self) -> list[str]:
        """
        Returns
        -------
        list[str]
            A list of conda environments.
        """

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


def GetPackageDict(env: str) -> dict[str, str]:
    """
    Parameters
    ----------
    env : str
        The name of the conda environment.

    Returns
    -------
    dict[str, str]
        A dictionary mapping package names to their versions.
    """

    result = subprocess.run(
        ["conda", "list", "-n", env, "--json"], stdout=subprocess.PIPE, text=True
    )

    pkgList = json.loads(result.stdout)
    pkgDict = {}

    for pkg in pkgList:
        pkgDict[pkg["name"]] = pkg["version"]

    return pkgDict


def UpdateEnv(env: str) -> subprocess.CompletedProcess:
    """
    Parameters
    ----------
    env : str
        The name of the conda environment.

    Returns
    -------
    subprocess.CompletedProcess
        The result of the subprocess call to update the environment.
    """

    return subprocess.run(
        ["conda", "update", "--all", "-n", env, "-y"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


if __name__ == "__main__":

    getEnvs = GetEnvs()
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
            preDict = GetPackageDict(env)
            console.print(Panel(f"[blue]{env}[/]: Updating dependencies"))

            result = UpdateEnv(env)

            postDict = GetPackageDict(env)

            table = Table(title=f"Environment: {env} Package Versions")
            table.add_column("Package", style="cyan")
            table.add_column("Old Version", style="yellow")
            table.add_column("New Version", style="green")

            allPkgs = set(preDict.keys()).union(postDict.keys())

            for pkg in sorted(allPkgs):
                oldVer = preDict.get(pkg, "-")
                newVer = postDict.get(pkg, "-")
                table.add_row(pkg, oldVer, newVer)

            if result.returncode == 0:
                console.print(
                    Panel(
                        f"[blue]{env}[/]: [green]Dependencies updated successfully[/]"
                    )
                )
                console.print(table)

            else:
                console.print(Panel(f"[blue]{env}[/]: [red]Update failed[/]"))
                console.print(Panel(result.stderr, title=f"{env} Error", style="red"))

            progress.advance(task)

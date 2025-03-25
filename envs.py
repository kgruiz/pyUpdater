import json
import re
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
TARGET_VERSION = "3.13.2"


class GetEnvs:
    """
    Callable class to retrieve a list of Conda environments.

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


def GetPackageDict(env: str) -> dict[str, str]:
    """
    Retrieve a dictionary of package names and versions for a given environment.

    Parameters
    ----------
    env : str
        The name of the Conda environment.

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


def GetPythonVersion(env: str) -> str:
    """
    Retrieve the Python version for a given environment.

    Parameters
    ----------
    env : str
        The name of the Conda environment.

    Returns
    -------
    str
        The Python version, or an empty string if not found.
    """

    result = subprocess.run(
        ["conda", "run", "-n", env, "python", "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    m = re.search(r"Python\s+(\S+)", result.stdout + result.stderr)
    return m.group(1) if m else ""


def UpgradeEnv(env: str) -> subprocess.CompletedProcess:
    """
    Upgrade the Python version in a given environment.

    Parameters
    ----------
    env : str
        The name of the Conda environment.

    Returns
    -------
    subprocess.CompletedProcess
        The result of the subprocess call.
    """

    return subprocess.run(
        [
            "conda",
            "install",
            "-n",
            env,
            f"python={TARGET_VERSION}",
            "--update-deps",
            "-y",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


if __name__ == "main":

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
        task = progress.add_task("Upgrading Python in environments", total=len(envs))

        for env in envs:
            preDict = GetPackageDict(env)
            currentVersion = GetPythonVersion(env)

            if not currentVersion:
                console.print(Panel(f"[yellow]{env}: No Python found[/]"))

                progress.advance(task)
                continue

            if currentVersion != TARGET_VERSION:
                console.print(
                    Panel(
                        f"[blue]{env}[/]: [yellow]{currentVersion}[/] → [green]{TARGET_VERSION}[/]"
                    )
                )
                result = UpgradeEnv(env)
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

                console.print(table)

            else:
                console.print(
                    Panel(f"[blue]{env}[/]: Already at [green]{TARGET_VERSION}[/]")
                )
                postDict = GetPackageDict(env)
                table = Table(title=f"Environment: {env} Package Versions (No Changes)")
                table.add_column("Package", style="cyan")
                table.add_column("Current Version", style="green")

                for pkg in sorted(postDict.keys()):
                    table.add_row(pkg, postDict[pkg])

                console.print(table)

            progress.advance(task)

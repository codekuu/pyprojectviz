from pathlib import Path
from datetime import datetime
import os
import typer

from pyprojectviz.config import load_config
from pyprojectviz.utils import generate_graph

app = typer.Typer()


@app.command()
def main(
    path: str = typer.Argument(
        ..., help="Path to the project to generate the graph for"
    ),
    output: str = typer.Option(None, help="Output file name"),
    config: str = typer.Option(None, help="Path to the configuration file"),
):
    if not output:
        date = datetime.now().strftime("%Y-%m_%d-%H-%M-%S")
        output = f"pyprojectviz-{date}"

    if not os.path.isdir(path):
        typer.echo("Invalid path to project")
        raise typer.Exit(code=1)

    config = load_config(config)

    project_path = Path(path).resolve()
    graph = generate_graph(project_path, config)

    output_path = Path(output).resolve()
    graph.render(output_path.as_posix(), view=False, cleanup=True, quiet=True)
    typer.echo(
        f"Graph generated at {output_path}.{config.graphviz.output_format}"
    )


if __name__ == "__main__":
    app()

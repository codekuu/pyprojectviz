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
    output_file: str = typer.Option(None, "--output", help="Output file name"),
    config_file: str = typer.Option(
        None, "--config", help="Path to the configuration file"
    ),
    keep_graph: bool = typer.Option(
        False, "--keep-graph", help="Keep the graphviz file after rendering"
    ),
):
    if not output_file:
        date = datetime.now().strftime("%Y-%m_%d-%H-%M-%S")
        output_file = f"pyprojectviz-{date}"

    if not os.path.isdir(path):
        typer.echo("Invalid path to project")
        raise typer.Exit(code=1)

    config = load_config(config_file)

    project_path = Path(path).resolve()
    graph = generate_graph(project_path, config)

    output_path = Path(output_file).resolve()
    graph.render(
        output_path.as_posix(),
        view=False,
        cleanup=not keep_graph and not config.keep_graph,
    )
    typer.echo(
        f"Graph generated at {output_path}.{config.graphviz.output_format}"
    )


if __name__ == "__main__":
    app()

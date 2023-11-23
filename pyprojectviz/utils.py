import ast
import glob
import graphviz
import os

from pyprojectviz.code_analyzer import CodeAnalyzer
from pyprojectviz.config import Configuration, GraphvizConfiguration


def parse_file(file_path, config: Configuration):
    with open(file_path, "r") as file:
        node = ast.parse(file.read())
    analyzer = CodeAnalyzer(config)
    analyzer.visit(node)
    return analyzer.graph


def load_graph(graphviz_conf: GraphvizConfiguration) -> graphviz.Digraph:
    graph = graphviz.Digraph(
        comment=graphviz_conf.comment,
        engine=graphviz_conf.layout_engine,
        format=graphviz_conf.output_format,
        graph_attr=graphviz_conf.graph_attr,
        node_attr=graphviz_conf.node_attr,
        edge_attr=graphviz_conf.edge_attr,
    )

    return graph


def generate_graph(
    project_path: str,
    config: Configuration,
):
    all_files = glob.glob(
        os.path.join(project_path, "**/*.py"), recursive=True
    )
    graph = load_graph(config.graphviz)
    for file in all_files:
        file_graph = parse_file(file, config)
        graph.subgraph(file_graph)
    return graph

import ast
import graphviz

from pyprojectviz.config import Configuration


class CodeAnalyzer(ast.NodeVisitor):
    """Analyzes the code of a Python project and generates a graph of its
    structure.
    """

    def __init__(self, config: Configuration):
        self.graph = graphviz.Digraph()
        self.current_class = None
        self.current_method = None
        self.config = config
        self.method_calls = []
        self.direct_imports = {}  # Track direct imports

    def visit_ImportFrom(self, node):
        """Track direct imports"""
        for alias in node.names:
            imported_name = alias.asname if alias.asname else alias.name
            if node.module in self.config.ignore_modules:
                self.direct_imports[imported_name] = node.module
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Add a node for each class"""
        if "self" in node.name:
            print(f"class def: {node.name}")
        if self._should_ignore_class(node.name):
            return
        self.add_class_node(node)

    def visit_FunctionDef(self, node):
        """Add a node for each method"""
        if "self" in node.name:
            print(f"function def: {node.name}")
        method_name = self._get_full_method_name(node.name)
        if self._should_ignore_method(method_name):
            return
        self.add_method_node(node, method_name)

    def visit_Call(self, node):
        """Add an edge for each method call"""
        root_module = self.get_root_module(node.func)
        call_name = self.extract_call_name(node.func)
        if self._should_ignore_method(call_name):
            return
        if self._should_ignore_method(root_module):
            return
        if self._should_ignore_call(root_module, call_name):
            return
        self.add_call_edge(node, root_module)

    def extract_call_name(self, node):
        """Extract the name of a call"""
        if isinstance(node, ast.Attribute):
            return node.attr
        elif isinstance(node, ast.Name):
            return node.id
        return None

    def get_root_module(self, node):
        """Get the root module of a call"""
        if isinstance(node, ast.Attribute):
            return self.get_root_module(node.value)
        elif isinstance(node, ast.Name):
            return node.id
        return None

    def add_class_node(self, node):
        """Add a node for each class"""
        class_label = node.name
        self.graph.node(
            node.name,
            label=class_label,
            **self.config.graphviz.class_node_attrs,
        )
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = None

    def add_method_node(self, node, method_name):
        """Add a node for each method"""
        method_label = method_name
        self.graph.node(
            method_name,
            label=method_label,
            **self.config.graphviz.method_node_attrs,
        )
        if self.current_class:
            self.graph.edge(self.current_class, method_name)
        self.current_method = method_name
        self.generic_visit(node)
        self.current_method = None

    def add_call_edge(self, node, root_module):
        """Add an edge for each method call"""
        if self.current_method is None:
            return  # Skip if there's no current method context

        full_call_name = self._get_full_method_name(root_module)
        if full_call_name is None:
            return  # Skip if the full call name couldn't be determined

        if self.current_method != full_call_name:
            self.graph.edge(self.current_method, full_call_name)

        self.generic_visit(node)

    def _should_ignore_class(self, class_name):
        """Check if a class should be ignored"""
        if not class_name:
            return True
        if class_name in self.config.ignore_classes:
            return True
        if self.direct_imports.get(class_name) in self.config.ignore_modules:
            return True

        return False

    def _should_ignore_method(self, method_name):
        """Check if a method should be ignored"""
        if not method_name:
            return True
        if method_name in self.config.ignore_methods:
            return True

        return False

    def _should_ignore_call(self, module_name, called_name):
        if not module_name or not called_name:
            return True
        # Ignore if the root module of the call is in ignored packages
        if module_name in self.config.ignore_modules:
            return True
        # Ignore if the called function is a direct import from ignored package
        if self.direct_imports.get(called_name) in self.config.ignore_modules:
            return True

        return False

    def _get_full_method_name(self, method_name):
        """Get the full name of a method"""
        if self.current_class:
            return f"{self.current_class}.{method_name}"
        return method_name

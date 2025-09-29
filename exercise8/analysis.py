import ast
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Record:
    scope: str
    target: str
    value_node: ast.AST
    expression: str


class DataFlowAnalyzer:
    """Extract simple data-flow information from a Python source file."""

    def __init__(self, file_name: str) -> None:
        self.source = Path(file_name).read_text()
        self.tree = ast.parse(self.source)
        self.assignment_map: dict[str, dict[str, ast.AST]] = {}
        self.assignment_records: list[Record] = []
        # self.operation_records: list[Record] = []

    def parse_assignments(self) -> None:
        """Collect assignment statements grouped by scope."""
        collector = _AssignmentCollector()
        collector.visit(self.tree)

        self.assignment_map = collector.assignment_map
        self.assignment_records = collector.records

    # def extract_assignment_operations(
    #     self, scope: Optional[str] = None
    # ) -> None:
    #     """Return assignments whose value is an operation (e.g., a binary op)."""
    #     operations: list[Record] = []
    #     for record in self.assignment_records:
    #         if isinstance(record.value_node, ast.BinOp) and (scope is None or record.scope == scope):
    #             operations.append(
    #                 Record(
    #                     scope=record.scope,
    #                     target=record.target,
    #                     value_node=record.value_node,
    #                     expression=record.expression,
    #                 )
    #             )

    #     self.operation_records = operations

    def generate_flow(self) -> str:
        """Produce a simple taint-style flow for the calculator example."""
        module_assigns = self.assignment_map.get("module", {})
        module_env: dict[str, any] = {}
        for name, value_node in module_assigns.items():
            try:
                module_env[name] = self._evaluate_literal(value_node)
            except ValueError:
                continue

        val2_value = module_env.get("val2")
        if val2_value is None:
            raise ValueError("Could not resolve the initial value for val2")

        flow_nodes: list[any] = [val2_value, "val2"]
        func_def = self._get_function_def("simpleCalculator")
        if func_def is None:
            raise ValueError("Function simpleCalculator not found")

        call_assign = self._find_function_call_assignment("simpleCalculator")
        if call_assign is None or not isinstance(call_assign.value, ast.Call):
            raise ValueError("Call to simpleCalculator not found")

        arg_values = [
            self._evaluate_expression(arg, module_env) for arg in call_assign.value.args
        ]
        param_names = [arg.arg for arg in func_def.args.args]
        param_env = dict(zip(param_names, arg_values))

        if param_env.get("v2") == val2_value:
            flow_nodes.append("v2")

        local_env = dict(param_env)
        res_value = self._evaluate_res_assignment(func_def, local_env)
        if res_value is None:
            raise ValueError("Could not resolve the value assigned to res")

        flow_nodes.append("res")
        flow_nodes.append(res_value)

        return "->".join(str(node) for node in flow_nodes)

    def run_pipeline(self) -> str:
        """Execute the pipeline: parse -> extract -> assignment -> output."""
        self.parse_assignments()
        # self.extract_assignment_operations()
        return self.generate_flow()

    def _evaluate_literal(self, node: ast.AST) -> any:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            operand = self._evaluate_literal(node.operand)
            return -operand
        if isinstance(node, ast.Tuple):
            return tuple(self._evaluate_literal(elt) for elt in node.elts)
        raise ValueError(f"Unsupported literal node: {ast.dump(node)}")

    def _evaluate_expression(self, node: ast.AST, env: dict[str, any]) -> any:
        if isinstance(node, ast.Name):
            if node.id in env:
                return env[node.id]
            raise KeyError(f"Unknown name: {node.id}")
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -self._evaluate_expression(node.operand, env)
        if isinstance(node, ast.BinOp):
            left = self._evaluate_expression(node.left, env)
            right = self._evaluate_expression(node.right, env)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            raise ValueError(f"Unsupported binary operation: {ast.dump(node.op)}")
        if isinstance(node, ast.Compare):
            return self._evaluate_compare(node, env)
        raise ValueError(f"Unsupported expression node: {ast.dump(node)}")

    def _evaluate_compare(self, node: ast.Compare, env: dict[str, any]) -> bool:
        left = self._evaluate_expression(node.left, env)
        right = self._evaluate_expression(node.comparators[0], env)
        op = node.ops[0]
        if isinstance(op, ast.Eq):
            return left == right
        if isinstance(op, ast.NotEq):
            return left != right
        raise ValueError(f"Unsupported comparison operator: {ast.dump(op)}")

    def _evaluate_res_assignment(
        self, func_def: ast.FunctionDef, env: dict[str, any]
    ) -> Optional[any]:
        for stmt in func_def.body:
            if isinstance(stmt, ast.Assign):
                value = self._handle_assignment(stmt, env)
                if value is not None:
                    return value
            elif isinstance(stmt, ast.If):
                branch = (
                    stmt.body
                    if self._evaluate_expression(stmt.test, env)
                    else stmt.orelse
                )
                for inner in branch:
                    if isinstance(inner, ast.Assign):
                        value = self._handle_assignment(inner, env)
                        if value is not None:
                            return value
                    elif isinstance(inner, ast.Return):
                        if inner.value is not None:
                            return self._evaluate_expression(inner.value, env)
                        return None
            elif isinstance(stmt, ast.Return):
                if stmt.value is not None:
                    return self._evaluate_expression(stmt.value, env)
                return None
        return None

    def _handle_assignment(
        self, node: ast.Assign, env: dict[str, any]
    ) -> Optional[any]:
        target_names = [_target_to_name(target) for target in node.targets]
        value = self._evaluate_expression(node.value, env)
        for name in target_names:
            if name is not None:
                env[name] = value
        if "res" in target_names and self._expression_contains_name(node.value, "v2"):
            return value
        return None

    def _expression_contains_name(self, node: ast.AST, target: str) -> bool:
        return any(
            isinstance(child, ast.Name) and child.id == target
            for child in ast.walk(node)
        )

    def _get_function_def(self, name: str) -> Optional[ast.FunctionDef]:
        for node in self.tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return node
        return None

    def _find_function_call_assignment(self, func_name: str) -> Optional[ast.Assign]:
        for node in self.tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                call = node.value
                if isinstance(call.func, ast.Name) and call.func.id == func_name:
                    return node
            if isinstance(node, ast.If):
                for stmt in node.body:
                    if isinstance(stmt, ast.Assign) and isinstance(
                        stmt.value, ast.Call
                    ):
                        call = stmt.value
                        if (
                            isinstance(call.func, ast.Name)
                            and call.func.id == func_name
                        ):
                            return stmt
        return None


def _assignment_pairs(targets: list[ast.expr], value: ast.AST) -> list[any]:
    pairs: list[any] = []
    if (
        len(targets) == 1
        and isinstance(targets[0], ast.Tuple)
        and isinstance(value, ast.Tuple)
    ):
        target_tuple = targets[0]
        if len(target_tuple.elts) == len(value.elts):
            pairs.extend(zip(target_tuple.elts, value.elts))
            return pairs
    for target in targets:
        pairs.append((target, value))
    return pairs


def _target_to_name(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    return None


def _to_source(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except AttributeError:
        return ast.dump(node)


class _AssignmentCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.assignment_map: dict[str, dict[str, ast.AST]] = defaultdict(dict)
        self.records: list[Record] = []
        self.scope_stack: list[str] = ["module"]

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.scope_stack.append(node.name)
        for stmt in node.body:
            self.visit(stmt)
        self.scope_stack.pop()

    def visit_Assign(self, node: ast.Assign) -> None:
        scope = self.scope_stack[-1]
        for target_node, value_node in _assignment_pairs(node.targets, node.value):
            target_name = _target_to_name(target_node)
            if target_name is None:
                continue
            self.assignment_map[scope][target_name] = value_node
            self.records.append(
                Record(
                    scope=scope,
                    target=target_name,
                    value_node=value_node,
                    expression=_to_source(value_node),
                )
            )


def main() -> None:
    data_flow_analyzer = DataFlowAnalyzer("calc.py")
    print(data_flow_analyzer.run_pipeline())


if __name__ == "__main__":
    main()

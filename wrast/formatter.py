import ast
import logging
import typing


log = logging.getLogger(__name__)


class Formatter:
    """
    Formats the provided source code back into proper Python code via AST.

    Inspired by `ast.NodeVisitor`.
    """

    _level: int = 0 
    _nls: int = 0

    def reformat(self, source: str) -> str:
        node: ast.AST = ast.parse(source)
        return self.format(node)

    def format(self, node: ast.AST) -> str:
        """Format a node."""
        method: str = 'format_' + node.__class__.__name__
        formatter: typing.Callable = getattr(self, method, self.generic_format)
        if formatter == self.generic_format:
            log.warn(node.__class__.__name__)
        return formatter(node)

    def generic_format(self, node: ast.AST) -> str:
        """Called if no explicit formatter function exists for a node."""
        formatted: typing.List[str] = []
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                formatted.append(self._generic_format_node_many(value))
            elif isinstance(value, ast.AST):
                formatted.append(self._generic_format_node_one(value))
        return ''.join(formatted)

    def _generic_format_node_many(self, nodes: typing.List[ast.AST]) -> str:
        return ''.join(
            self.format(node) for node in nodes if isinstance(node, ast.AST))

    def _generic_format_node_one(self, node: ast.AST) -> str:
        return self.format(node)

    def format_Num(self, node: ast.Num) -> str:
        return f'{node.n}'

    def format_Str(self, node: ast.Str) -> str:
        s = node.s
        if '\n' in s:
            return f"'''{s}'''"
        else:
            return f"'{s}'"

    def format_Module(self, node: ast.Module) -> str:
        self._level = 0
        return self.generic_format(node)

    def format_For(self, node: ast.For) -> str:
        line = f'for {self.format(node.target)} in {self.format(node.iter)}'
        return self._format_container(line=line, body=node.body)

    def format_Name(self, node: ast.Name) -> str:
        return f'{node.id}'

    def format_Call(self, node: ast.Call) -> str:
        arg_list = []
        for arg in node.args:
            arg_list.append(self.format(arg))
        for keyword in node.keywords:
            arg_list.append(self.format(keyword))
        return f'{self.format(node.func)}({", ".join(arg_list)})'

    def format_Expr(self, node: ast.Expr) -> str:
        return self._format_block(block=f'{self.format(node.value)}')

    def format_Assign(self, node: ast.Assign) -> str:
        targets = ' = '.join(self.format(target) for target in node.targets)
        return self._format_block(
            block=f'{targets} = {self.format(node.value)}')

    def format_While(self, node: ast.While) -> str:
        return self._format_container(
            line=f'while {self.format(node.test)}', body=node.body)

    def format_Compare(self, node: ast.Compare) -> str:
        right = ' '.join(
            f'{self.format(x[0])} {self.format(x[1])}'
            for x in zip(node.ops, node.comparators))
        return f'{self.format(node.left)} {right}'

    def format_Lt(self, node: ast.Lt) -> str:
        return '<'

    def format_AugAssign(self, node: ast.AugAssign) -> str:
        f = self.format
        return self._format_block(
            block=f'{f(node.target)} {f(node.op)}= {f(node.value)}')

    def format_Add(self, node: ast.Add) -> str:
        return '+'

    def _format_container(self, *, line: str, body: list) -> str:
        start = self._format_container_start()
        formatted_body = '\n'.join(self.format(node) for node in body)
        end = self._format_container_end()
        return self._format_block(block=f'{start}{line}:\n{formatted_body}{end}')

    def _format_container_start(self) -> str:
        self._level += 1
        if not self._nls:
            self._nls += 1
        return ''

    def _format_container_end(self) -> str:
        self._level -= 1
        formatted_nls = '\n' * self._nls
        self._nls = 0
        return formatted_nls

    def _format_block(self, *, block: str) -> str:
        return f'{self._format_offset()}{block}'

    def _format_offset(self) -> str:
        return ' ' * 4 * self._level

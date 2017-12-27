import ast
import logging
import typing
import tokenize
import io
import collections

log = logging.getLogger(__name__)
TokensType = typing.Deque[tokenize.TokenInfo]


class Formatter:
    """
    Formats the provided source code back into proper Python code via AST.

    Inspired by `ast.NodeVisitor`.
    """

    _level: int = 0 
    _nls: int = 0

    def reformat(self, source: str) -> str:
        node: ast.AST = ast.parse(source)
        tokens: TokensType = collections.deque(
            x
            for x in tokenize.tokenize(io.BytesIO(source.encode()).readline)
            if x.type in (tokenize.COMMENT, tokenize.NL))
        return self.format(node, tokens)

    def format(self, node: ast.AST, tokens: TokensType) -> str:
        """Format a node."""
        log.debug(node.__class__.__name__)
        method: str = 'format_' + node.__class__.__name__
        formatter: typing.Callable = getattr(self, method, self.generic_format)
        return formatter(node, tokens)

    def generic_format(self, node: ast.AST, tokens: TokensType) -> str:
        """Called if no explicit formatter function exists for a node."""
        formatted: typing.List[str] = [f'<{node.__class__.__name__}>']
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                formatted.append(
                    ''.join(
                        self.format(node, tokens)
                        for node in nodes
                        if isinstance(node, ast.AST)))
            elif isinstance(value, ast.AST):
                formatted.append(self.format(node, tokens))
        return ''.join(formatted)

    def format_Module(self, node: ast.Module, tokens: TokensType) -> str:
        self._level = 0

        formatted = []

        for block in node.body:

            while tokens:
                token = tokens.popleft()

                if token.start[0] >= block.lineno:
                    tokens.appendleft(token)
                    break

                formatted.append(token.string)

            formatted.append(f'{self.format(block, tokens)}\n')

        return ''.join(formatted)

    def format_Num(self, node: ast.Num, tokens: TokensType) -> str:
        return f'{node.n}'

    def format_Str(self, node: ast.Str, tokens: TokensType) -> str:
        s = node.s
        if '\n' in s:
            return f"'''{s}'''"
        else:
            return f"'{s}'"

    def format_For(self, node: ast.For, tokens: TokensType) -> str:
        line = (
            f'for {self.format(node.target, tokens)}'
            f' in {self.format(node.iter, tokens)}')
        return self._format_container(line=line, body=node.body)

    def format_Name(self, node: ast.Name, tokens: TokensType) -> str:
        return f'{node.id}'

    def format_Call(self, node: ast.Call, tokens: TokensType) -> str:
        arg_list = []
        for arg in node.args:
            arg_list.append(self.format(arg, tokens))
        for keyword in node.keywords:
            arg_list.append(self.format(keyword, tokens))
        return f'{self.format(node.func, tokens)}({", ".join(arg_list)})'

    def format_Expr(self, node: ast.Expr, tokens: TokensType) -> str:
        return self._format_block(block=f'{self.format(node.value, tokens)}')

    def format_Assign(self, node: ast.Assign, tokens: TokensType) -> str:
        targets = ' = '.join(
            self.format(target, tokens) for target in node.targets)
        return self._format_block(
            block=f'{targets} = {self.format(node.value, tokens)}')

    def format_While(self, node: ast.While, tokens: TokensType) -> str:
        return self._format_container(
            line=f'while {self.format(node.test, tokens)}', body=node.body)

    def format_Compare(self, node: ast.Compare, tokens: TokensType) -> str:
        right = ' '.join(
            f'{self.format(x[0], tokens)} {self.format(x[1], tokens)}'
            for x in zip(node.ops, node.comparators))
        return f'{self.format(node.left, tokens)} {right}'

    def format_Lt(self, node: ast.Lt, tokens: TokensType) -> str:
        return '<'

    def format_AugAssign(self, node: ast.AugAssign, tokens: TokensType) -> str:
        f = self.format
        return self._format_block(
            block=f'{f(node.target)} {f(node.op)}= {f(node.value)}')

    def format_Add(self, node: ast.Add, tokens: TokensType) -> str:
        return '+'

    def _format_container(
        self, *, line: str, body: list, tokens: TokensType
    ) -> str:
        start = self._format_container_start()
        formatted_body = '\n'.join(self.format(node, tokens) for node in body)
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

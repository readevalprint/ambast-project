import ast
import codegen


expr="""
def foo():
   print("hello world")
"""
p=ast.parse(expr)

p.body[0].body = [ast.parse("return 42").body[0]]
print(ast.dump(p, False))
print(codegen.to_source(p))


class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


def ast_walk(node, func=None, depth=0):
    if not func:
        func = lambda x: x
    tab = (depth * "    ") + "%s"
    d = {}
    if isinstance(node, ast.AST):
        node = func(node)
        for k, v in node.__dict__.items():
            if k in node._fields:
                d[k] = ast_walk(v, func=func, depth=depth+1)
        return {str(node.__class__): d}

    elif isinstance(node, list):
        return [ast_walk(i, func=func, depth=depth+1) for i in node]
    else:
        return node

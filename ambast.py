import ast
import codegen
from collections import *
import itertools


class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


def serialize(node, depth=0):
    d = {}
    if isinstance(node, ast.AST):
        for k, v in node.__dict__.items():
            if k in node._fields:
                d[k] = serialize(v, depth=depth + 1)
        return (node.__class__, d)

    elif isinstance(node, list):
        return [serialize(i, depth=depth + 1) for i in node]
    else:
        return node


def deserialize(node):
    if isinstance(node, tuple):
        klass, kws = node
        return klass(**deserialize(kws))
    elif isinstance(node, dict):
        d = {}
        for k, v in node.items():
            d[k] = deserialize(v)
        return d
    elif isinstance(node, list):
        return [deserialize(n) for n in node]
    else:
        return node


def thousand_monkeys(cls, source_nodes, depth=0):
    node_options = source_nodes[cls]
    for option in node_options:
        d = {}
        for k, v in option.items():
            if getattr(v, '__module__', '') == '_ast':
                if depth > 0:
                    d[k] = list(thousand_monkeys(v, source_nodes, depth - 1))
                else:
                    d[k] = v()
            elif isinstance(v, list):
                d[k] = v
            else:
                d[k] = v
        yield cls(**d)


def powerset(iterable, l):
    s = list(i for i in iterable) * l
    return chain.from_iterable([permutations(s, r) for r in range(1, l + 1)])


from collections import defaultdict


def option_generator(node):
    node_dict = defaultdict(set)
    meta = defaultdict(set)
    for n in ast.walk(node):
        for k in n._fields:
            f = getattr(n, k)
            if isinstance(f, list):
                node_dict[k] |= set(ff.__class__ for ff in f)
                meta['nodes'] |= node_dict[k]
                meta['lists'] |= set([k])
            elif getattr(f, '__module__', '') == '_ast':
                node_dict[k] |= set([f.__class__])
                meta['nodes'] |= set([f.__class__])
            else:
                node_dict[k] |= set([f])
    return dict(node_dict), dict(meta)


def kwarg_expander(cls, options, meta, depth=5):
    if depth > 0 and getattr(cls, '__module__', '') == '_ast':
        multi_kwargs = dict((f, options[f]) for f in cls()._fields)
        field_lists = []
        for field, sub_nodes in multi_kwargs.iteritems():
            print field, sub_nodes
            sub_field_lists = []
            for sub_node in sub_nodes:
                sub_node = kwarg_expander(sub_node, options, meta, depth=depth - 1)
                if field in meta['lists']:
                    sub_node_product = sum([list(itertools.product(*([sub_node] * n))) for n in range(1, depth+1)], [])
                    sub_field_lists += [(field, o) for o in (list(p) for p in  sub_node_product)]
                else:
                    sub_field_lists += [(field, o) for o in sub_node]
            field_lists += [sub_field_lists]
        kwarg_list = [dict(d) for d in itertools.product(*field_lists)]
        return [(cls, l) for l in kwarg_list]
    if getattr(cls, '__module__', '') == '_ast':
        return [(cls, {})]
    return [cls]


def set_generator(options):
    def wrapper():
        for o in options:
            yield o
    return wrapper


def doubles(node, **kwargs):
    d = {}
    if isinstance(node, ast.AST):
        for k, v in node.__dict__.items():
            if k in node._fields:
                d[k] = doubles(v, parent=node)
        l = list(dict(d) for d in itertools.product(*[[(k,vv) for vv in v] for k, v in d.iteritems()]))



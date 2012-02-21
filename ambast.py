import ast
import codegen
import itertools
from collections import defaultdict
import pprint

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




def option_generator(node):
    node_dict = defaultdict(dict)
    meta = defaultdict(dict)
    for n in ast.walk(node):
        for k in n._fields:
            if 'nodes' not in meta[n.__class__]:
                node_dict[n.__class__] = defaultdict(set)
                meta[n.__class__]['nodes'] = set()
                meta[n.__class__]['lists'] = set()
            f = getattr(n, k)
            if isinstance(f, list):
                node_dict[n.__class__][k] |= set(ff.__class__ for ff in f)
                meta[n.__class__]['nodes'] |= node_dict[n.__class__][k]
                meta[n.__class__]['lists'] |= set([k])
            elif getattr(f, '__module__', '') == '_ast':
                node_dict[n.__class__][k] |= set([f.__class__])
                meta[n.__class__]['nodes'] |= set([f.__class__])
            else:
                node_dict[n.__class__][k] |= set([f])
            node_dict[n.__class__]['ctx'] = set([None])
            if not node_dict[n.__class__][k]:
                node_dict[n.__class__][k] = set([None])
    return dict(node_dict), dict(meta)

import functools
import cPickle
def memoize(fctn):
        memory = {}
        @functools.wraps(fctn)
        def memo(*args,**kwargs):
                haxh = cPickle.dumps((args, sorted(kwargs.iteritems())))

                if haxh not in memory:
                        memory[haxh] = fctn(*args,**kwargs)

                return memory[haxh]
        if memo.__doc__:
            memo.__doc__ = "\n".join([memo.__doc__,"This function is memoized."])
        return memo

def kwarg_expander(cls, options, meta, height=1, width=3, depth=5, parent_cls=None):
    if not parent_cls:
        parent_cls = cls
    if depth > 0 and getattr(cls, '__module__', '') == '_ast':
        multi_kwargs = dict((f, options[cls][f]) for f in cls()._fields)
        field_lists = []
        for field, sub_nodes in multi_kwargs.iteritems():
            # print field, sub_nodes
            sub_field_lists = []
            for sub_node in sub_nodes:
                sub_node = kwarg_expander(sub_node, options, meta, height=height, width=width, depth=depth - 1, parent_cls=cls)
                if field in meta[cls]['lists']:
                    min_width = 1
                    if cls is ast.BoolOp:
                        min_width = 2
                        width = 2
                    if field == 'body':
                        width = height
                    sub_node_product = sum([list(itertools.product(*([sub_node] * n))) for n in range(min_width, width+1)], [])
                    sub_field_lists += [(field, o) for o in (list(p) for p in  sub_node_product)]
                else:
                    sub_field_lists += [(field, o) for o in sub_node]
            field_lists += [sub_field_lists]
        kwarg_list = [dict(d) for d in itertools.product(*field_lists)]
        return [(cls, l) for l in kwarg_list]
    if getattr(cls, '__module__', '') == '_ast':
        return []
    return [cls]


def possible(code, height=1, width=2, depth=4):
    p = ast.parse(code)
    options, meta = option_generator(p)
    return kwarg_expander(ast.Module, options, meta, height=height, width=width, depth=depth)



def print_possible(k):
    for i in k:
        print '#' * 10
        try:
            d = deserialize(i)
            print codegen.to_source(d)
        except Exception as e:
            print e



def test_possible(k, templete, data, out):
    for i in k:
        print '#' * 10
        try:
            d = deserialize(i)
            c = codegen.to_source(d)
            print c
            ns = {'data': data, 'out': out, 'good': False}
            exec (templete % c) in ns
            if ns['good']:
                yield c
        except Exception as e:
            print e


## {{{ http://code.activestate.com/recipes/483752/ (r1)
import threading
class TimeoutError(Exception): pass

def timelimit(timeout):
    def internal(function):
        def internal2(*args, **kw):
            class Calculator(threading.Thread):
                def __init__(self):
                    threading.Thread.__init__(self)
                    self.result = None
                    self.error = None

                def run(self):
                    try:
                        self.result = function(*args, **kw)
                    except:
                        self.error = sys.exc_info()[0]

            c = Calculator()
            c.start()
            c.join(timeout)
            if c.isAlive():
                raise TimeoutError
            if c.error:
                raise c.error
            return c.result
        return internal2
    return internal
## end of http://code.activestate.com/recipes/483752/ }}}


from graphviz import Digraph

def trace(root):
    """Walks through the computational graph starting from a given node,
    traces back all the input nodes and returns a list of nodes in the
    topological order of the graph."""
    nodes, edges = set(), set()
    def build(v):
        if v not in nodes:
            nodes.add(v)
            for child in v._prev:
                edges.add((child, v))
                build(child)
    build(root)
    return nodes, edges

def draw_dot(root, format='svg', rankdir='LR', output_filepath=None):
    """
    format: png | svg | ...
    rankdir: TB (top to bottom graph) | LR (left to right)
    """
    assert rankdir in ['LR', 'TB']
    nodes, edges = trace(root)
    dot = Digraph(format=format, graph_attr={'rankdir': rankdir}) #, node_attr={'rankdir': 'TB'})
    
    for n in nodes:
        dot.node(name=str(id(n)), label = f"{n.data:.2f} | {n.grad:.2f}", shape='record')
        if n._op:
            dot.node(name=str(id(n)) + n._op, label=n._op)
            # operator -> output
            dot.edge(str(id(n)) + n._op, str(id(n)))
    
    for n1, n2 in edges:
        dot.edge(str(id(n1)), str(id(n2)) + n2._op)
    
    if output_filepath != None:
        dot.render(output_filepath, view=False)
    return dot
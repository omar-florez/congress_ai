# Import library
from d3graph import d3graph, vec2adjmat

# Create example network
source = ['node A','node F','node B','node B','node B','node A','node C','node Z']
target = ['node F','node B','node J','node F','node F','node M','node M','node A']
weight = [5.56, 0.5, 0.64, 0.23, 0.9, 3.28, 0.5, 0.45]
# Convert to adjacency matrix
adjmat = vec2adjmat(source, target, weight=weight)

# Initialize
d3 = d3graph()
# Proces adjmat
d3.graph(adjmat)
# Plot
d3.show()

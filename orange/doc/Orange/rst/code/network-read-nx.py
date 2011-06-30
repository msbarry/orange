import Orange.network

from matplotlib import pyplot as plt

# read network from file
net = Orange.network.readwrite.read("K5.net")

# network layout object to work with network coordinates
net_layout = Orange.network.GraphLayout()
net_layout.set_graph(net)

# read all edges and plot a line
for u, v in net.edges():
    x1, y1 = net_layout.coors[0][u], net_layout.coors[1][u]
    x2, y2 = net_layout.coors[0][v], net_layout.coors[1][v]
    plt.plot([x1, x2], [y1, y2], 'b-')

# read x and y coordinates to Python list
x = net_layout.coors[0]
y = net_layout.coors[1]

# plot vertices
plt.plot(x, y, 'ro')
plt.savefig("network-read.py.png")

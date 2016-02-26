import silk
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import bipartite


class GraphBuilder(object):
    graph = None

    def __init__(self, file_name, sip):
        self.sip = silk.IPAddr(sip)

        self.silk_file = silk.silkfile_open(file_name, silk.READ)

    def _create_graph(self):
        self.graph = nx.Graph()
        for rec in self.silk_file:
            if rec.sip == self.sip:
                self.graph.add_node(rec.dip, bipartite=0)
                self.graph.add_node(rec.dport, bipartite=1)
                self.graph.add_edge(rec.dip, rec.dport)

    def show_graph(self):
        if self.graph is None:
            self._create_graph()
        ports, ips = bipartite.sets(self.graph)
        pos = dict()
        pos.update((n, (1, i)) for i, n in enumerate(ips))
        pos.update((n, (2, i)) for i, n in enumerate(ports))
        nx.draw(self.graph, pos, with_labels=True)
        plt.show()

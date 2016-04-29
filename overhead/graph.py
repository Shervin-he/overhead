import silk
import networkx as nx
import matplotlib.pyplot as plt


class GraphBuilder(object):
    graph = None

    def __init__(self, file_name, sip):
        self.sip = silk.IPAddr(sip)

        self.silk_file = silk.silkfile_open(file_name, silk.READ)

    def _create_graph(self):
        self.graph = nx.Graph()
        for rec in self.silk_file:
            if rec.sip == self.sip:
                self.graph.add_node(rec.dip.padded(), bipartite=0)
                self.graph.add_node(rec.dport, bipartite=1)
                self.graph.add_edge(rec.dip.padded(), rec.dport)

    def show_graph(self):
        if self.graph is None:
            self._create_graph()
        ips = set(n for n, d in self.graph.nodes(data=True) if d['bipartite'] == 0)
        ports = set(n for n, d in self.graph.nodes(data=True) if d['bipartite'] == 1)
        pos = dict()

        for i in ips:
                pos[i] = [p for p in ports if self.graph.has_edge(i, p)]
        pos.update((n, (1, i)) for i, n in enumerate(ips))
        pos.update((n, (2, i)) for i, n in enumerate(ports))
        nx.draw(self.graph, pos, with_labels=True)
        plt.show()

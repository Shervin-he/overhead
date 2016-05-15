import argparse
from overhead import __version__
from overhead import graph
from overhead.analyze import Analyzer
import json

COMMAND_CHOICES = (
    'show-graph', 'verticalfactors', 'centrality', 'pagerank', 'clustering-coefficient', 'spectrum',
    'eccentricity-factors', 'basic-info', 'connected-components', 'degree-distribution', 'edge-overlap')


def main():
    # TODO: get disc from setup?
    parser = argparse.ArgumentParser(description="A network scan detector based on analysis of netflow data.")
    parser.add_argument('-v', '--version', action='version', version='overhead v %s' % __version__,
                        help="Prints the program's version")
    parser.add_argument('command', choices=COMMAND_CHOICES, help='The action you want to run.')
    parser.add_argument('silk_file', help="Raw flow data file for silk")
    parser.add_argument('ip', help="The source IP of the graph.")
    args = parser.parse_args()
    if args.command == 'show-graph':
        g_builder = graph.GraphBuilder(args.silk_file, args.ip)
        g_builder.show_graph()

    if args.command == 'verticalfactors':
        analyzer = Analyzer(args.silk_file, args.ip)
        analyzer.print_factors()

    if args.command == 'centrality':
        g_builder = graph.GraphBuilder(args.silk_file, args.ip)
        print 'clossness centrality: ' + json.dumps(g_builder.get_closeness_centrality())
        print 'betweenness centrality: ' + json.dumps(g_builder.get_betweenness_centrality())
        print 'eigenvector centrality: ' + json.dumps(g_builder.get_eigenvector_centrality())
        print 'edge betweenness centrality: ', g_builder.get_edge_betweenness_centrality()

    if args.command == 'pagerank':
        g_builder = graph.GraphBuilder(args.silk_file, args.ip)
        print g_builder.get_page_rank()

    if args.command == 'clustering-coefficient':
        g_builder = graph.GraphBuilder(args.silk_file, args.ip)
        print g_builder.get_average_clustring_coefficient()

    if args.command == 'spectrum':
        g_builder = graph.GraphBuilder(args.silk_file, args.ip)
        print g_builder.get_spectrum()

    if args.command == 'eccentricity-factors':
        g_builder = graph.GraphBuilder(args.silk_file, args.ip)
        print 'center: ', g_builder.get_center_node()
        print 'radius: ', g_builder.get_radius()
        print 'diameter: ', g_builder.get_diameter()

    if args.command == 'basic-info':
        g_builder = graph.GraphBuilder(args.silk_file, args.ip)
        print 'node count:', g_builder.get_node_count()
        print 'edge count:', g_builder.get_edge_count()
        print 'density:', g_builder.get_density()

    if args.command == 'connected-components':
        g_builder = graph.GraphBuilder(args.silk_file, args.ip)
        print g_builder.get_connected_component_count()

    if args.command == 'degree-distribution':
        g_builder = graph.GraphBuilder(args.silk_file, args.ip)
        g_builder.draw_degree_plot()

    if args.command == 'edge-overlap':
        g_builder = graph.GraphBuilder(args.silk_file, args.ip)
        print g_builder.get_edge_overlap()


if __name__ == '__main__':
    main()

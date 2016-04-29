import argparse
from overhead import __version__
from overhead import graph
from overhead.analyze import Analyzer

COMMAND_CHOICES = ('show-graph', 'verticalfactors')


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
        analyser = Analyzer(args.silk_file, args.ip)
        analyser.print_factors()

if __name__ == '__main__':
    main()

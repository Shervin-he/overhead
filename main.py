import argparse
from overhead import __version__

COMMAND_CHOICES = ('show-graph', 'gephi')


def main():
    # TODO: get disc from setup?
    parser = argparse.ArgumentParser(description="A network scan detector based on analysis of netflow data.")
    parser.add_argument('-v', '--version', action='version', version='overhead v %s' % __version__,
                        help="Prints the program's version")
    parser.add_argument('command', choices=COMMAND_CHOICES, help='The action you want to run.')
    args = parser.parse_args()
    if args.command == 'gephi':
        print "Output for Gephi"
    print "here we go again."

if __name__ == '__main__':
    main()

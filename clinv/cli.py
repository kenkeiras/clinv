import logging
import argparse
import argcomplete


def load_parser():
    ''' Configure environment '''

    # Argparse
    parser = argparse.ArgumentParser(
        description="Command line asset inventory"
    )

    parser.add_argument(
        "-d",
        "--data_path",
        type=str,
        default='~/.local/share/clinv',
        help='Path to the inventory',
    )
    subparser = parser.add_subparsers(dest='subcommand', help='subcommands')

    search_parser = subparser.add_parser('search')
    search_parser.add_argument(
        "search_string",
        type=str,
        help='String used to search',
    )

    subparser.add_parser('generate')

    unassigned_parser = subparser.add_parser('unassigned')
    unassigned_parser.add_argument(
        "resource_type",
        type=str,
        help='String used to search',
        choices=['ec2', 'services', 'informations'],
    )

    argcomplete.autocomplete(parser)
    return parser


def load_logger():
    logging.addLevelName(logging.INFO, "[\033[36mINFO\033[0m]")
    logging.addLevelName(logging.ERROR, "[\033[31mERROR\033[0m]")
    logging.addLevelName(logging.DEBUG, "[\033[32mDEBUG\033[0m]")
    logging.addLevelName(logging.WARNING, "[\033[33mWARNING\033[0m]")
    logging.basicConfig(level=logging.WARNING,
                        format="  %(levelname)s %(message)s")

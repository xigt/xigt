
import argparse

from xigt.scripts import (
    xigt_export,
    xigt_import,
    xigt_process,
    xigt_query,
    xigt_validate
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'command',
        choices=('export', 'import', 'process', 'query', 'validate')
    )
    parser.add_argument(
        'args',
        nargs=argparse.REMAINDER
    )

    args = parser.parse_args()
    if args.command == 'export':
        xigt_export.main(args.args)
    elif args.command == 'import':
        xigt_import.main(args.args)
    elif args.command == 'process':
        xigt_process.main(args.args)
    elif args.command == 'query':
        xigt_query.main(args.args)
    elif args.command == 'validate':
        xigt_validate.main(args.args)


if __name__ == '__main__':
    main()
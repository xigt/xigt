
import argparse

from xigt.scripts import (
    xigt_export,
    xigt_import,
    xigt_partition,
    xigt_process,
    xigt_sort,
    xigt_query,
    xigt_validate
)

cmdmap = {
    'export': xigt_export,
    'import': xigt_import,
    'partition': xigt_partition,
    'process': xigt_process,
    'sort': xigt_sort,
    'query': xigt_query,
    'validate': xigt_validate,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'command',
        choices=sorted(cmdmap.keys())  # sorted for help printing
    )
    parser.add_argument(
        'args',
        nargs=argparse.REMAINDER
    )

    args = parser.parse_args()
    cmdmap[args.command].main(args.args)


if __name__ == '__main__':
    main()


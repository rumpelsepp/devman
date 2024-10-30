# SPDX-FileCopyrightText: Stefan Tatschner
#
# SPDX-License-Identifier: MIT

import argparse
import subprocess
import sys
from importlib import metadata
from pprint import pprint

import argcomplete

from devman import config
from devman import podman


def parse_args(conf: config.Config) -> tuple[argparse.Namespace, argparse.ArgumentParser]:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-c",
        "--container",
        default=conf.get_value(
            "devman.default_container", "ghcr.io/rumpelsepp/devman:master",
        ),
        help="specify container image for all commands",
    )
    parser.add_argument(
        "--mount",
        action="append",
        default=conf.get_value("devman.mounts"),
        help="mount directory in $HOME into the container"
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="show parsed config file and exit",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f'%(prog)s {metadata.version("devman")}',
    )

    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser("run", help="run command in devman container")
    run_parser.add_argument(
        "CMD",
        nargs="?",
        default=conf.get_value(
            "devman.run.default_command",
            podman.get_default_cmd(),
        ),
        help="command to run",
    )
    run_parser.add_argument(
        "--ssh",
        action=argparse.BooleanOptionalAction,
        default=conf.get_value("devman.run.ssh", False),
        help="enable/disable ssh agent and credentials within the devman",
    )
    run_parser.add_argument(
        "--gui",
        default=conf.get_value("devman.run.gui", False),
        action=argparse.BooleanOptionalAction,
        help="enable/disable support for wayland applications within the devman",
    )
    run_parser.add_argument(
        "--term",
        default=conf.get_value("devman.run.share_term", True),
        action=argparse.BooleanOptionalAction,
        help="enable/disable sharing TERM variable with container",
    )
    run_parser.add_argument(
        "--debug",
        action="store_true",
        help="show podman arguments and exit",
    )
    run_parser.set_defaults(command="run")

    pull_parser = subparsers.add_parser("pull", help="pull configured container")
    pull_parser.set_defaults(command="pull")

    argcomplete.autocomplete(parser)

    return parser.parse_args(), parser


def cmd_run(args: argparse.Namespace) -> int:
    podman_args = podman.create_args(args.container, ssh=args.ssh, gui=args.gui, term=args.term, mounts=args.mount)
    invocation = ["podman", "run"] + podman_args + [args.CMD]

    if args.debug:
        pprint(invocation)
        return 0

    p = subprocess.run(invocation, check=False)
    return p.returncode


def cmd_pull(args: argparse.Namespace) -> int:
    p = subprocess.run(
        ["podman", "pull", args.container],
        check=False,
    )

    return p.returncode


def run() -> None:
    conf, config_path = config.load_config_file("devman.toml")
    args, parser = parse_args(conf)
    exitcode = 0

    if args.show_config:
        if config_path is not None:
            print(f"config loaded from: {config_path}", file=sys.stderr)
            pprint(conf)
            sys.exit(0)
        else:
            print("no config available", file=sys.stderr)
            sys.exit(1)

    if "command" not in args:
        parser.error("no command specified")

    match args.command:
        case "run":
            exitcode = cmd_run(args)
        case "pull":
            exitcode = cmd_pull(args)
        case _:
            raise RuntimeError("BUG: unreachable code")

    sys.exit(exitcode)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass
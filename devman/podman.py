# SPDX-FileCopyrightText: Stefan Tatschner
#
# SPDX-License-Identifier: MIT

import os
from pathlib import Path


def env_flag(env_name: str, default: str | None = None) -> list[str]:
    if (s := os.environ.get(env_name)) is not None:
        return ["--env", f"{env_name}={s}"]
    if default is not None:
        return ["--env", f"{env_name}={default}"]
    return []


def volume_flag(src: str, dst: str | None = None, flag: str | None = None) -> list[str]:
    dst = src if dst is None else dst
    arg = f"{src}:{dst}"
    if flag is not None:
        arg = f"{arg}:{flag}"
    return ["--volume", arg]


def volume_flag_from_env(name: str, flag: str | None = None) -> list[str]:
    if (s := os.environ.get(name)) is not None:
        return volume_flag(s, flag=flag)
    return []


def get_default_cmd() -> str:
    if (s := os.getenv("SHELL")) is not None:
        return s
    return "/bin/sh"


def create_mount_arg(raw: str) -> list[str]:
    home = Path.home()
    container_home = Path("/home/dev")

    parts = raw.split(":", maxsplit=2)
    hostdir = Path(parts[0])
    if not hostdir.is_absolute():
        hostdir = home.joinpath(hostdir)
    flags = None

    match len(parts):
        case 3:
            containerdir = Path(parts[1])
            flags = parts[2]
        case 2:
            containerdir = Path(parts[1])
        case 1:
            containerdir = container_home.joinpath(hostdir.relative_to(home))
        case _:
            raise RuntimeError("BUG: unreachable code")

    if not containerdir.is_absolute():
        containerdir = container_home.joinpath(containerdir)

    volume_arg = f"{hostdir}:{containerdir}"
    if flags is not None:
        volume_arg += f":{flags}"

    return ["--volume", volume_arg]


def create_args(
    container: str,
    mounts: list[str] | None,
    expose: list[str] | None,
    ssh: bool,
    gui: bool,
    term: bool,
) -> list[str]:
    cwd = Path.cwd()
    home = Path.home()
    container_home = Path("/home/dev")
    container_cwd = container_home.joinpath("CWD").joinpath(cwd.name)

    args = [
        "--rm",
        "--interactive",
        "--tty",
    ]
    args += ["--workdir", str(container_cwd)]
    args += ["--volume", f"{cwd}:{container_cwd}"]
    args += [
        "--tmpfs",
        "/tmp:rw,size=787448k,mode=1777",
    ]  # TODO: calculate size somehow?
    args += ["--log-driver", "none"]
    args += ["--hostname", "devman"]

    args += ["--group-add", "keep-groups"]
    args += ["--userns", "keep-id:uid=1000,gid=1000"]

    args += env_flag("COLORTERM")
    args += env_flag("EDITOR")
    args += env_flag("TERM_PROGRAM")
    args += env_flag("TERM_PROGRAM_VERSION")
    args += env_flag("SHELL")
    args += env_flag("TERMINFO")
    args += env_flag("XDG_RUNTIME_DIR")
    args += volume_flag_from_env("XDG_RUNTIME_DIR")

    if term:
        args += env_flag("TERM")

    if ssh:
        args += env_flag("SSH_AUTH_SOCK")
        args += volume_flag_from_env("SSH_AUTH_SOCK")
        args += volume_flag(f"{home}/.ssh", f"{container_home}/.ssh", flag="O")

    if gui:
        args += env_flag("ELECTRON_OZONE_PLATFORM_HINT", default="auto")
        args += env_flag("XDG_SESSION_CLASS")
        args += env_flag("XDG_SESSION_DESKTOP")
        args += env_flag("XDG_CURRENT_DESKTOP")
        args += env_flag("XDG_MENU_PREFIX")
        args += env_flag("XDG_SESSION_TYPE")
        args += env_flag("WAYLAND_DISPLAY")
        args += env_flag("DBUS_SESSION_BUS_ADDRESS")
        args += ["--device", "/dev/dri"]

    if mounts is not None:
        for mount in mounts:
            args += create_mount_arg(mount)
    if expose is not None:
        for port in expose:
            args += ["--expose", port]

    return args + [container]

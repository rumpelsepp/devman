<!--
SPDX-FileCopyrightText: Stefan Tatschner
SPDX-License-Identifier: CC0-1.0
-->

# devman

A tool for **dev**elopment using pod**man**.
Create simple development containers with easy access to the host filesystem using a correct user id mapping.
Features such as sharing SSH config (e.g. SSH agent) or starting GUI applications from the container are supported.

## Install

On the system level, the [`podman`](https://podman.io/) and the [catatonit](https://github.com/openSUSE/catatonit) tools are required.
They are available and packaged for a large number of systems.
Please refer to the official manual containing [install instructions](https://podman.io/docs/installation).

On Debian, this bails down to:

```
$ sudo apt install podman catatonit
```

### pipx

```
$ pipx install devman
```

### uv

`devman` can be run without installation using the [uv](https://github.com/astral-sh/uv) tool:

```
$ uvx devman
```

## Quickstart

Ready to use containers with a lot of pre-installed development tools are provided by the Github container registry associated with this repo.

Pull the default Debian container (the `Containerfile` is located in this repository in `containers/debian/`):

```
$ devman pull
```

Start a `fish` shell in a container:

```
$ devman run fish
```

The current directory `DIR` from the host is mounted in the container at `/home/dev/CWD/DIR`.
The user `dev` corresponds to the user that invoked `devman`.

If you would like to share your SSH config with the container, add `--ssh`.
If you want to be able to start GUI applications from the container, add `--gui`.

## `podman` Performance

For performance reason you could consider using native overlay mounts.
Make sure that the following is included in your storage configuration.

```
$ cat ~/.config/containers/storage.conf
[storage]
driver = "overlay"
```


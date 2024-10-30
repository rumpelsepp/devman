# SPDX-FileCopyrightText: Stefan Tatschner
#
# SPDX-License-Identifier: MIT


from devman import cli

try:
    cli.run()
except KeyboardInterrupt:
    pass

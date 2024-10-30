# SPDX-FileCopyrightText: Stefan Tatschner
#
# SPDX-License-Identifier: MIT

import argparse
import os
import subprocess
import sys
from importlib import metadata
from pathlib import Path

from devman import cli


try:
    cli.run()
except KeyboardInterrupt:
    pass

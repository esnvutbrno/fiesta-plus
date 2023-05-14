#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
from __future__ import annotations

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fiesta.settings")
    os.environ.setdefault("DJANGO_CONFIGURATION", "Development")
    from configurations.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

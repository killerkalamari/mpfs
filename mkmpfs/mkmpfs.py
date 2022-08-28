#!/usr/bin/env python3
# mkmpfs.py: Create a mpfs (MicroPython file system) in a script compatible with
#            Casio MicroPython 1.9.4.
# Copyright (C) 2022  Jeffry Johnston
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import os
import czip

# These characters can be entered on the calculator during input(), excluding
# ` ' and `"'
FILENAME_CHARS = "()*+,-./0123456789=ABCDEFGHIJKLMNOPQRSTUVWXYZ[]"\
                 "abcdefghijklmnopqrstuvwxyz{}"

# Parse command line arguments
if len(sys.argv) < 2:
	sys.exit(f"Usage: {sys.argv[0]} FILE... >MODULE.py")
paths = sys.argv[1:]

# Add files
files: list[str] = []
for path in paths:
	# Read file
	with open(path, "rb") as f:
		data = f.read()

	# Add directory entry
	filename = os.path.basename(path)
	for c in filename:
		if c not in FILENAME_CHARS:
			sys.exit(
				f"The filename `{filename}' contains disallowed character `{c}'"
			)

	czip_str = czip.create(data)
	files.append(f"\"{filename}\":({len(data)},{czip_str})")

# Create file system
files_str = ",".join(files)
mpfs = "MPFS={" + files_str + "}\n"

# Write output
sys.stdout.buffer.write(mpfs.encode("latin1"))

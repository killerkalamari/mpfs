#!/usr/bin/env python3
# czip.py: Compress a file to a script compatible with Casio MicroPython 1.9.4.
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

FORMAT_RAW = 0
FORMAT_LZSS = 2

import sys
import lzss

def to_python_str(data: list[int], reserved_extra: list[int]=[]):
    """
    Create a string that does not contain any of the following characters:
        \n, \r, \", \\
    Return a string of the form:
        REPLACEMENT_CHARACTER chr(RESERVED_CHARACTER_CODE + 128)
    And return a string with all reserved characters replaced or escaped.

    Escape sequences will be of the form:
        ESCAPE_CHARACTER chr(CHARACTER_CODE_TO_BE_ESCAPED + 128) % 256)

    Keyword arguments:
    data --           List of integer character codes, each in the range
                      [0, 255] or containing codes from reserved_extra
    reserved_extra -- List of codes to reserve, each in the range [-128, 127]
                      and none of: -36, -94, -115, -118
    """

    # The reserved characters, as well as an escape character and any bytes from
    # `reserved_extra' will be replaced with characters chosen from either
    # unused or the least used bytes in `data'. Then, those replaced characters
    # will in turn also either be replaced with unused characters or escaped.
    # This scheme aims to minimize the number of escape sequences actually used.

    # List of reserved bytes potentially needing replacement
    reserved: list[int]=[10, 13, 34, 92]

    # Check reserved_extra and append each entry to reserved
    extra_to_reserve = len(reserved_extra) + 1 # Add one for an escape character
    for entry in reserved_extra:
        if entry < -128 or entry > 127 or entry + 128 in reserved:
            raise ValueError(
                f"reserved_extra entry `{entry}' was either outside the range "\
                f"[-128, 127] or entry + 128 ({entry + 128}) was not any of "\
                f"the values in this list: {reserved}"
            )
    reserved.extend(reserved_extra)

    # Count the number of times each byte is used in data
    dist: dict[int, int] = {}
    for i in range(256):
        dist[i] = 0
    for i in data:
        if (i < 0 and i not in reserved_extra) or i > 255:
            raise ValueError(
                f"data value `{i}' was outside the range [0, 255] and not any "\
                f"of the values in this list: {reserved_extra}")
        if i >= 0 and i < 256:
            dist[i] += 1

    # Sort the results into a list, with the least used bytes first
    sorted_dist = sorted(dist.items(), key=lambda x: x[1])

    # Reserve additional codes for escaping and reserved_extra
    sorted_i = 0
    while True:
        item = sorted_dist[sorted_i][0]
        sorted_i += 1
        if item not in reserved and item < 128:
            reserved.append(item)
            extra_to_reserve -= 1
            if extra_to_reserve <= 0:
                break
    escape = reserved[-1]

    # Find replacements for reserved bytes
    replacements_str = ""
    replacements: dict[int, list[int]] = {}
    reserved_new = reserved[:]
    for item in reserved:
        if item >= 0 and dist[item] == 0:
            continue
        while True:
            replacement = sorted_dist[sorted_i][0]
            sorted_i += 1
            if replacement not in reserved_new and \
                (replacement + 128) % 256 not in reserved_new:
                reserved_new.append(replacement)
                replacements_str += chr(replacement) + chr(item + 128)
                replacements[item] = [replacement]
                replacements[replacement] = [escape, (replacement + 128) % 256]
                break

    # Perform replacement and escaping
    output = ""
    for i in data:
        try:
            for r in replacements[i]:
                output += chr(r)
        except:
            output += chr(i)

    return replacements_str, output

def create(data: bytes) -> str:
    # Original data (RAW)
    original_data = list(data)
    replacements, python_str = to_python_str(original_data)
    data_len = len(replacements) + len(python_str)
    fmt = FORMAT_RAW

    # LZSS
    lzss_compressed_data = lzss.compress(original_data)
    decompressed_data = lzss.decompress(lzss_compressed_data)
    if decompressed_data != original_data:
        sys.exit("LZSS compression error!")
    lzss_replacements, lzss_python_str = to_python_str(
        lzss_compressed_data, [lzss.LZSS_SEQUENCE_INDICATOR]
    )
    lzss_len = len(lzss_replacements) + len(lzss_python_str)
    if lzss_len < data_len:
        replacements = lzss_replacements
        python_str = lzss_python_str
        data_len = lzss_len
        fmt = FORMAT_LZSS

    # Convert to Python string
    czip_str = f"{fmt},b\"{replacements}\",b\"{python_str}\""

    return czip_str

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) != 2:
        sys.exit(f"Usage: {sys.argv[0]} INPUT_FILENAME >OUTPUT_FILENAME.czip")
    filename_in = sys.argv[1]

    # Read file
    with open(filename_in, "rb") as f:
        var_str = "czip=(" + create(f.read()) + ")\n"

    # Write output
    sys.stdout.buffer.write(var_str.encode("latin1"))

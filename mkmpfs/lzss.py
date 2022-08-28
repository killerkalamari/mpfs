#!/usr/bin/env python3
# lzss.py: LZSS compression/decompression routines
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

LZSS_WINDOW_SIZE = 1024
LZSS_MIN_SEQ_LEN = 4
LZSS_SEQUENCE_INDICATOR = -1

def compress(data_in: list[int]) -> list[int]:
	data_out: list[int] = []
	window: list[int] = [0] * LZSS_WINDOW_SIZE

	i = 0
	while i < len(data_in):
		current_offset = best_offset = -1
		best_length = -1
		i2 = 0

		# Brute force search the window for the longest matching sequence,
		# against sequences starting at the current offset. There will probably
		# be multiple matching sequences in the window, so keep track of the
		# best one and continue until the entire window has been searched.
		for j in range(LZSS_WINDOW_SIZE):
			if current_offset == -1:
				if window[j] == data_in[i]:
					current_offset = j
					i2 = i + 1
			else:
				# End of sequence
				# 1) End of input data
				# 2) Data mismatch
				# 3) Sequence too long
				if i2 >= len(data_in) or window[j] != data_in[i2] \
						or (i2 - i) > 62 + LZSS_MIN_SEQ_LEN:
					current_length = j - current_offset
					if current_length > best_length:
						best_offset = current_offset
						best_length = current_length
					current_offset = -1
				else:
					i2 += 1

		# Only replace the original data if storing the offset/length is smaller
		if best_length >= LZSS_MIN_SEQ_LEN:
			window_data = data_in[i: i + best_length]
			data_out.extend([
				LZSS_SEQUENCE_INDICATOR,
				best_offset & 0xFF,
				(best_length - LZSS_MIN_SEQ_LEN) | ((0x300 & best_offset) >> 2)
			])
		else:
			window_data = [data_in[i]]
			data_out.append(data_in[i])

		i += len(window_data)
		window = window[len(window_data):]
		window.extend(window_data)

	return data_out

def decompress(data_in: list[int]) -> list[int]:
	data_out: list[int] = []
	window: list[int] = [0] * LZSS_WINDOW_SIZE

	i = 0
	while i < len(data_in):
		value = data_in[i]
		if value == LZSS_SEQUENCE_INDICATOR:
			b1 = data_in[i + 1]
			b2 = data_in[i + 2]
			offset = b1 | (b2 & 0xC0) << 2
			length = (b2 & 0x3F) + LZSS_MIN_SEQ_LEN
			window_data = window[offset: offset + length]
			data_out.extend(window_data)
			i += 3
		else:
			window_data = [value]
			data_out.append(value)
			i += 1
		window = window[len(window_data):]
		window.extend(window_data)

	return data_out

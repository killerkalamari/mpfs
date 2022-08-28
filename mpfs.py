# type: ignore
SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

class FileNotFoundError(OSError):
    def __init__(self, path):
        super().__init__("No such file: '{0}'".format(path))

class Czip:
	def reset(self):
		self.pos = 0

	def read(self):
		try:
			i = self.data[self.pos]
			self.pos += 1
			if i == self.escape:
				b = (self.data[self.pos] - 128) % 256
				self.pos += 1
			elif i in self.replacements:
				b = self.replacements[i]
			else:
				b = i
		except IndexError:
			return -128
		return b

	def __init__(self, file):
		r_str = file[2]
		self.data = file[3]
		self.replacements = {}
		for i in range(0, len(r_str), 2):
			self.replacements[r_str[i]] = r_str[i + 1] - 128
		self.escape = r_str[-1] - 128
		self.reset()

class Lzss(Czip):
	def reset(self):
		super().reset()
		self.window = [0] * 1024 # LZSS_WINDOW_SIZE
		self.buf = []

	def read(self):
		if len(self.buf) < 1:
			i = super().read()
			if i == -1: # LZSS_SEQUENCE_INDICATOR
				offset = super().read()
				length = super().read()
				offset |= (length & 0xC0) << 2
				length = (length & 0x3F) + 4 # LZSS_MIN_SEQ_LEN
				window_data = self.window[offset: offset + length]
				self.buf = window_data
			else:
				self.buf = window_data = [i]
			self.window = self.window[len(window_data):]
			self.window.extend(window_data)
		return self.buf.pop(0)

class Mpfs:
	def _reset(self):
		self._pos = 0
		self._czip.reset()

	def read(self, n=-1):
		if self.closed:
			raise ValueError("file is closed")
		if n == 0:
			return b""
		data = []
		while True:
			b = self._czip.read()
			if b < 0:
				break
			data.append(b)
			self._pos += 1
			if n > 0 and len(data) >= n:
				break
		return bytes(data)

	def readline(self):
		line = []
		while True:
			c = self.read(1)
			if len(c) < 1:
				break
			c = chr(c[0])
			line.append(c)
			if c == "\n":
				break
		return "".join(line)

	def readlines(self):
		lines = []
		while True:
			line = self.readline()
			if len(line) < 1:
				break
			lines.append(line)
		return lines

	def seek(self, offset, whence=SEEK_SET):
		if whence == 0:
			pos = offset
		elif whence == 1:
			pos = self._pos + offset
		elif whence == 2:
			pos = self._size + offset
		else:
			raise ValueError("invalid whence")
		if pos < 0:
			raise ValueError("negative seek position: " + str(offset))
		if pos >= self._pos:
			self.read(pos - self._pos)
		else:
			self._reset()
			self.read(pos)
		self._pos = pos
		return pos

	def tell(self):
		return self._pos

	def close(self):
		self.closed = True
		try:
			del self._czip
		except NameError:
			pass

	def __iter__(self):
		return self

	def __next__(self):
		line = self.readline()
		if len(line) < 1:
			raise StopIteration
		return line

	def __enter__(self):
		return self

	def __exit__(self, *_):
		self.close()

	def __init__(self, file):
		self._size = file[0]
		format = file[1]
		if format == 0: # FORMAT_RAW
			self._czip = Czip(file)
		elif format == 2: # FORMAT_LZSS
			self._czip = Lzss(file)
		else:
			raise ValueError("unknown file format: " + str(format))
		self._reset()
		self.closed = False

def mount(module):
	global MPFS
	try:
		del MPFS
	except KeyError:
		pass
	MPFS = __import__(module).MPFS

def open(filename):
	try:
		file = MPFS[filename]
	except KeyError:
		raise FileNotFoundError(filename)
	return Mpfs(file)

def remove(filename):
	try:
		del MPFS[filename]
	except:
		raise FileNotFoundError(filename)

def listdir(_):
	return list(MPFS)

def getsize(filename):
	try:
		return MPFS[filename][0]
	except:
		raise FileNotFoundError(filename)

def exists(filename):
	return filename in MPFS

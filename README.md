# mpfs: MicroPython File System

## Rationale

The MicroPython 1.9.4 implementation for Casio calculators does not currently
provide a working open() call nor os module. The `mpfs` module works around
those limitations by mounting a transparently-compressed read-only file system
that is accessible to user scripts. It provides the most useful methods of the
file object and equivalents for several functions in os and os.path.

## Installation

Run the following command to install mkmpfs: ```sudo ./install.sh```

Then, copy the ```mpfs.py``` module to the Casio calculator's USB storage.

To uninstall mkmpfs, run ```sudo ./uninstall.sh```.

## Build a file system

The ```mkmpfs``` program will compress the source files and build a file system.
For example, to create a Python module named `test` with a file system
containing the data from files `a.txt` and `data/b.dat`, run:

```
mkmpfs a.txt data/b.dat >test.py
```

The file system does not support a directory structure. In the
above command, data is read from `data/b.dat`, however the file will be
named `b.dat` inside the file system.

## Import mpfs

The recommended way to import the mpfs module is:

```
import mpfs;from mpfs import open
```

## Mount a file system

If the file system is named ```test.py``` then the Python module name will be
```test```. Mount the file system with this command:

```
mpfs.mount("test")
```

Although ```mount()``` may be called multiple times, only one file system may be
mounted at a time. Each subsequent call replaces the prior file system.

Remounting a file system will not restore removed files; restart the program
instead.

## File operations

### Read a text file

```
>>> with open("a.txt") as f:
...     for line in f:
...         print(line, end="")
...
Abc
defgh
ijk.
```

Other file methods to read lines from a file are ```readline()``` and
```readlines()```:

```
>>> with open("a.txt") as f:
...     f.readline()
...     f.readlines()
...
'Abc\n'
['defgh\n', 'ijk.\n']
```

More information:
- https://docs.python.org/3/library/functions.html#open
- https://docs.python.org/3/library/io.html#io.IOBase
- https://docs.python.org/3/library/io.html#io.IOBase.readline
- https://docs.python.org/3/library/io.html#io.IOBase.readlines

### Read a binary file

```
>>> with open("b.dat") as f:
...     data = f.read(10)
...
>>> data
b'\x02\x80@\x80?\xe0\x0f\xf8\x03\xfe'
```

Rather than reading 10 bytes, the entire file could have been be read at once
using ```f.read()```. However, with large files there may be insufficient
memory to do so. Instead, read and process fewer bytes at a time. Depending on
the situation, it may be helpful to make use of Python's ```yield``` keyword.

More information:
- https://docs.python.org/3/library/functions.html#open
- https://docs.python.org/3/library/io.html#io.IOBase
- https://docs.python.org/3/library/io.html#io.RawIOBase.read

### Get or set current file position

```
>>> with open("a.txt") as f:
...     f.readline()
...     f.tell()
...     f.seek(0)
...     f.readline()
...     f.seek(-3, mpfs.SEEK_END)
...     f.read()
...
'Abc\n'
4
0
'Abc\n'
12
b'k.\n'
```

More information:
- https://docs.python.org/3/library/io.html#io.IOBase.seek
- https://docs.python.org/3/library/io.html#io.IOBase.tell

## File system information

### List files

```
>>> mpfs.listdir("")
['a.txt', 'b.dat']
```

More information:
- https://docs.python.org/3/library/os.html#os.listdir

### Get uncompressed file size, in bytes

```
>>> mpfs.getsize("a.txt")
15
```

More information:
- https://docs.python.org/3/library/os.path.html#os.path.getsize

### Determine whether a file exists

```
>>> mpfs.exists("c.txt")
False
```

More information:
- https://docs.python.org/3/library/os.path.html#os.path.exists

## Delete a file

Although the file system is read-only, when a file system is mounted it (and all
the files it contains) will be copied to Python's heap, taking up space. If a
file is no longer needed, it can be removed to free up some heap space. The
files are not permanently deleted and will return the next time the program is
run.

```
>>> mpfs.listdir("")
['a.txt', 'b.dat']
>>> mpfs.remove("b.dat")
>>> mpfs.listdir("")
['a.txt']
```

More information:
- https://docs.python.org/3/library/os.html#os.remove

## Indices

### Internal functions and builtin replacements

- mpfs.mount(module: str) -> None
- open(filename: str) -> mpfs.Mpfs

More information:
- https://docs.python.org/3/library/functions.html#open

### Mpfs file object methods

- close() -> None
- read(n: int=-1) -> bytes()
- readline() -> str
- readlines() -> list[str]
- seek(offset: int, whence: int=mpfs.SEEK_SET) -> int
- seek(offset: int, mpfs.SEEK_CUR) -> int
- seek(offset: int, mpfs.SEEK_END) -> int
- tell() -> int

More information:
- https://docs.python.org/3/library/io.html#io.IOBase
- https://docs.python.org/3/library/io.html#io.RawIOBase

### Function equivalents for the os module

- mpfs.listdir(_) -> list[str]
- mpfs.remove(filename: str) -> None

More information:
- https://docs.python.org/3/library/os.html#files-and-directories

### Function equivalents for the os.path module

- mpfs.exists(filename) -> bool
- mpfs.getsize(filename) -> int

More information:
- https://docs.python.org/3/library/os.path.html#module-os.path

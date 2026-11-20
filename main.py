#!/usr/bin/env python3
"""Copy the 20 November 2026 front page to the output directory.

The front page itself is drawn in advance and shipped beside this
program as entry.png (see README.md for the stories it covers).
This program only copies that file to $MAKEFUN_OUTPUT_DIR/entry.png,
checks the copy is byte-for-byte identical, and refuses to write
anything bigger than the 1 MiB gate limit. Standard library only,
no network.
"""
import hashlib
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576  # the competition's 1 MiB gate limit
MAX_SIDE = 1024  # the competition's 1024x1024 gate limit
PNG_MAGIC = b"\x89PNG"


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def png_dimensions(data):
    """Read width and height from the PNG IHDR chunk (bytes 16-24)."""
    if len(data) < 24 or data[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")

    with open(SOURCE, "rb") as handle:
        data = handle.read()
    if len(data) > MAX_BYTES:
        print("entry.png is %d bytes, over the 1 MiB limit" % len(data),
              file=sys.stderr)
        return 1
    if not data.startswith(PNG_MAGIC):
        print("entry.png is not a PNG file", file=sys.stderr)
        return 1
    dims = png_dimensions(data)
    if dims is None:
        print("entry.png has no readable IHDR chunk", file=sys.stderr)
        return 1
    if dims[0] > MAX_SIDE or dims[1] > MAX_SIDE:
        print("entry.png is %dx%d, over the 1024x1024 limit" % dims,
              file=sys.stderr)
        return 1

    with open(dest, "wb") as handle:
        handle.write(data)
    with open(dest, "rb") as handle:
        written = handle.read()
    if sha256_hex(written) != sha256_hex(data):
        print("output does not match entry.png", file=sys.stderr)
        return 1

    print("wrote %s (%d bytes, sha256 %s)" % (dest, len(written),
                                              sha256_hex(written)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

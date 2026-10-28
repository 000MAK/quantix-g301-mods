r"""Build quantix_logo.bin from the stock G301 logo partition (backup\logo.bin): the three GENERAL MOBILE
splash images (0, 2, 38) are replaced with quantix_logo.png; every other image is copied byte for byte.

MTK logo format: 512-byte header (magic 0x58881688, body size, "logo"), then body = count, total size,
offset table, and one zlib stream per image (720x1560 BGRA).

    F:\Quantix_Master_Vault\simba_desktop_companion\.venv\Scripts\python.exe make_logo.py
Flash (bootloader unlocked):  fastboot flash logo quantix_logo.bin
Undo:                         fastboot flash logo ..\backup\logo.bin
"""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
STOCK = HERE.parent / "backup" / "logo.bin"
W, H = 720, 1560
REPLACE = (0, 2, 38)


def split(data: bytes) -> tuple[bytes, list[bytes]]:
    magic, size = struct.unpack_from("<II", data, 0)
    assert magic == 0x58881688, "not an MTK logo partition"
    body = data[512:512 + size]
    count, total = struct.unpack_from("<II", body, 0)
    offs = list(struct.unpack_from(f"<{count}I", body, 8)) + [total]
    return data[:512], [body[offs[i]:offs[i + 1]] for i in range(count)]


def join(header: bytes, blobs: list[bytes], part_size: int) -> bytes:
    table = 8 + 4 * len(blobs)
    offs, pos = [], table
    for b in blobs:
        offs.append(pos)
        pos += len(b)
    body = struct.pack(f"<II{len(blobs)}I", len(blobs), pos, *offs) + b"".join(blobs)
    out = bytearray(header)
    struct.pack_into("<I", out, 4, len(body))
    out += body
    assert len(out) <= part_size, "logo does not fit the partition"
    return bytes(out) + b"\0" * (part_size - len(out))


def main() -> None:
    stock = STOCK.read_bytes()
    header, blobs = split(stock)
    assert join(header, blobs, len(stock))[:512 + struct.unpack_from("<I", stock, 4)[0]] == \
        stock[:512 + struct.unpack_from("<I", stock, 4)[0]], "round-trip mismatch"
    img = Image.open(HERE / "quantix_logo.png").convert("RGBA").resize((W, H))
    new = zlib.compress(img.tobytes("raw", "BGRA"), 9)
    for i in REPLACE:
        assert len(zlib.decompress(blobs[i])) == W * H * 4
        blobs[i] = new
    out = join(header, blobs, len(stock))
    (HERE / "quantix_logo.bin").write_bytes(out)
    check = Image.frombytes("RGBA", (W, H), zlib.decompress(split(out)[1][0]), "raw", "BGRA")
    check.convert("RGB").resize((240, 520)).save(HERE / "quantix_logo_check.png")
    print("ok", len(out), "bytes")


if __name__ == "__main__":
    main()

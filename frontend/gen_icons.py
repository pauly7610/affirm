import struct, zlib

def make_png(w, h, r, g, b):
    raw = b''
    for _ in range(h):
        raw += b'\x00' + bytes([r, g, b, 255]) * w
    compressed = zlib.compress(raw)
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)

    def chunk(chunk_type, data):
        c = chunk_type + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', ihdr)
            + chunk(b'sRGB', b'\x00')
            + chunk(b'IDAT', compressed)
            + chunk(b'IEND', b''))

# Affirm blue: #3B6BF5
with open('assets/icon.png', 'wb') as f:
    f.write(make_png(1024, 1024, 59, 107, 245))

with open('assets/favicon.png', 'wb') as f:
    f.write(make_png(48, 48, 59, 107, 245))

print("Generated icon.png and favicon.png")

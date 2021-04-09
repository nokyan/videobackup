import hashlib


def sha1_file(input_file: str):
    """Computes the SHA-1 hash of an input file"""
    h  = hashlib.sha1()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(input_file, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.digest()


def clamp(val, min, max):
    """Clamps a value between a maximum and a minimum value"""
    if val < min: return min
    if val > max: return max
    return val
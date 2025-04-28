# lib/utils.py

import hashlib

def calculate_sha256(file_path: str) -> str:
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                sha256.update(block)
        return sha256.hexdigest()
    except Exception as e:
        print(f"[Utils] Error calculando checksum: {e}")
        return ""

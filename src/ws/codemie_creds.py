"""Read, decrypt and re-encrypt CodeMie CLI SSO credential files.

Mirrors ``CredentialStore`` in ``codemie-ai/codemie-code``
(``src/utils/security.ts``). The on-disk credential file is encrypted with a
key derived solely from the machine identity string
``os.hostname() + os.platform() + os.arch()`` (Node's values), so a file
written on one machine cannot be read on another. ``rewrap`` decrypts with the
source identity and re-encrypts with a target identity, which is what lets a
host credential be used inside a Linux container.
"""

from __future__ import annotations

import hashlib
import json
import platform
import socket
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Node os.platform() / os.arch() vocabularies we map the host's Python values to.
_NODE_PLATFORM = {"Darwin": "darwin", "Linux": "linux", "Windows": "win32"}
_NODE_ARCH = {
    "arm64": "arm64",
    "aarch64": "arm64",
    "x86_64": "x64",
    "amd64": "x64",
}

_GCM_IV_LEN = 12
_GCM_TAG_LEN = 16
_CREDENTIALS_SUBDIR = "credentials"
_FALLBACK_FILE = "sso-credentials.enc"
_CONFIG_FILE = "codemie-cli.config.json"


@dataclass(frozen=True)
class MachineIdentity:
    """The three values CodeMie feeds into its key derivation."""

    hostname: str
    node_platform: str
    node_arch: str

    @classmethod
    def for_host(cls) -> "MachineIdentity":
        system = platform.system()
        machine = platform.machine().lower()
        if system not in _NODE_PLATFORM:
            raise ValueError(f"unsupported host platform: {system!r}")
        if machine not in _NODE_ARCH:
            raise ValueError(f"unsupported host architecture: {machine!r}")
        return cls(socket.gethostname(), _NODE_PLATFORM[system], _NODE_ARCH[machine])

    def key(self) -> bytes:
        machine_id = f"{self.hostname}{self.node_platform}{self.node_arch}"
        # security.ts: key = sha256( sha256(machineId).hexdigest() )
        inner = hashlib.sha256(machine_id.encode()).hexdigest()
        return hashlib.sha256(inner.encode()).digest()


def decrypt(blob: str, identity: MachineIdentity) -> str:
    """Decrypt an ``iv:tag:ciphertext`` (GCM) or legacy ``iv:ciphertext`` (CBC) blob."""
    parts = blob.strip().split(":")
    key = identity.key()
    if len(parts) == 3:
        iv, tag, ct = (bytes.fromhex(p) for p in parts)
        return AESGCM(key).decrypt(iv, ct + tag, None).decode()
    if len(parts) == 2:
        # Legacy AES-256-CBC. Imported lazily; only very old files use it.
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

        iv, ct = (bytes.fromhex(p) for p in parts)
        dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
        padded = dec.update(ct) + dec.finalize()
        return padded[: -padded[-1]].decode()
    raise ValueError(f"unrecognised credential blob format ({len(parts)} parts)")


def encrypt(text: str, identity: MachineIdentity) -> str:
    """Encrypt to the ``iv:tag:ciphertext`` GCM form CodeMie writes."""
    import os

    iv = os.urandom(_GCM_IV_LEN)
    sealed = AESGCM(identity.key()).encrypt(iv, text.encode(), None)
    ct, tag = sealed[:-_GCM_TAG_LEN], sealed[-_GCM_TAG_LEN:]
    return f"{iv.hex()}:{tag.hex()}:{ct.hex()}"


def _credential_files(codemie_home: Path) -> list[Path]:
    found: list[Path] = []
    cred_dir = codemie_home / _CREDENTIALS_SUBDIR
    if cred_dir.is_dir():
        found.extend(sorted(cred_dir.glob("sso-*.enc")))
    fallback = codemie_home / _FALLBACK_FILE
    if fallback.is_file():
        found.append(fallback)
    return found


def rewrap(
    src_home: Path,
    dst_home: Path,
    source: MachineIdentity,
    target: MachineIdentity,
) -> list[dict]:
    """Re-encrypt every SSO credential file from ``source`` identity to ``target``.

    Writes files with identical relative names under ``dst_home`` and copies the
    profile config. Returns one summary dict per credential file.
    """
    files = _credential_files(src_home)
    if not files:
        raise FileNotFoundError(
            f"no SSO credential files under {src_home} — the credential may be "
            "keychain-only; run `codemie profile login` so a file is written"
        )

    summaries: list[dict] = []
    for path in files:
        payload = json.loads(decrypt(path.read_text(), source))
        rel = path.relative_to(src_home)
        out_path = dst_home / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(encrypt(json.dumps(payload), target))
        summaries.append(
            {
                "file": str(rel),
                "cookies": sorted(payload.get("cookies", {})),
                "apiUrl": payload.get("apiUrl"),
                "expiresAt": payload.get("expiresAt"),
            }
        )

    src_config = src_home / _CONFIG_FILE
    if src_config.is_file():
        (dst_home / _CONFIG_FILE).write_text(src_config.read_text())

    return summaries

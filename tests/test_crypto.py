"""Tests for envault.crypto encryption/decryption utilities."""

import pytest
from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-passphrase"
PLAINTEXT = "DATABASE_URL=postgres://user:pass@localhost/db"


def test_encrypt_returns_string():
    token = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(token, str)
    assert len(token) > 0


def test_encrypt_produces_different_tokens():
    """Each encryption should produce a unique token due to random salt/nonce."""
    token1 = encrypt(PLAINTEXT, PASSWORD)
    token2 = encrypt(PLAINTEXT, PASSWORD)
    assert token1 != token2


def test_decrypt_roundtrip():
    token = encrypt(PLAINTEXT, PASSWORD)
    result = decrypt(token, PASSWORD)
    assert result == PLAINTEXT


def test_decrypt_wrong_password_raises():
    token = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(token, "wrong-password")


def test_decrypt_invalid_token_raises():
    with pytest.raises(ValueError):
        decrypt("not-a-valid-token!!", PASSWORD)


def test_decrypt_truncated_token_raises():
    with pytest.raises(ValueError, match="too short"):
        import base64
        short = base64.urlsafe_b64encode(b"tooshort").decode()
        decrypt(short, PASSWORD)


def test_encrypt_empty_string():
    token = encrypt("", PASSWORD)
    result = decrypt(token, PASSWORD)
    assert result == ""


def test_encrypt_unicode_plaintext():
    text = "API_KEY=\u6d4b\u8bd5\u5bc6\u94a5"
    token = encrypt(text, PASSWORD)
    result = decrypt(token, PASSWORD)
    assert result == text

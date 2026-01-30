"""Tests for og_pilot.jwt_encoder module."""

import jwt
import pytest

from og_pilot.jwt_encoder import ALGORITHM, encode


class TestJwtEncoder:
    """Tests for JWT encoding."""

    def test_encode_creates_valid_jwt(self):
        """Test that encode creates a valid JWT."""
        payload = {"title": "Test", "template": "default"}
        secret = "test-secret-key"

        token = encode(payload, secret)

        # Verify it's a valid JWT
        assert token.count(".") == 2

        # Decode and verify payload
        decoded = jwt.decode(token, secret, algorithms=[ALGORITHM])
        assert decoded["title"] == "Test"
        assert decoded["template"] == "default"

    def test_encode_uses_hs256(self):
        """Test that encoding uses HS256 algorithm."""
        payload = {"test": "data"}
        secret = "secret"

        token = encode(payload, secret)

        # Decode without verification to check header
        header = jwt.get_unverified_header(token)
        assert header["alg"] == "HS256"

    def test_encode_with_complex_payload(self):
        """Test encoding with nested payload."""
        payload = {
            "title": "Complex Test",
            "metadata": {"author": "Test Author", "tags": ["tag1", "tag2"]},
            "iss": "example.com",
            "sub": "test1234",
        }
        secret = "test-secret"

        token = encode(payload, secret)
        decoded = jwt.decode(token, secret, algorithms=[ALGORITHM])

        assert decoded["title"] == "Complex Test"
        assert decoded["metadata"]["author"] == "Test Author"
        assert decoded["metadata"]["tags"] == ["tag1", "tag2"]

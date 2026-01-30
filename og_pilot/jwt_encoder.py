"""
OG Pilot JWT Encoder

JWT encoding utilities using HS256 algorithm.
"""

import jwt


ALGORITHM = "HS256"


def encode(payload: dict, secret: str) -> str:
    """
    Encode a payload as a JWT token using HS256 algorithm.

    Args:
        payload: Dictionary containing the JWT claims
        secret: Secret key for signing

    Returns:
        Encoded JWT token string
    """
    return jwt.encode(payload, secret, algorithm=ALGORITHM)

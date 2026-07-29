import hmac
import hashlib
import base64
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger("orchestrator.auth.jwt")

SECRET_KEY = "KinNestSecretOrchestratorKeyForFamilyPartitionSecurity"

def hash_password(password: str) -> str:
    """Returns SHA256 hashed password with a static salt for local database persistence."""
    return hashlib.sha256((password + "KinNestSalt").encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies standard hashed passwords match plain text queries."""
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a standard compliant base64url signed token (compatible with standard JWT structural parts)."""
    payload = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
        
    payload["exp"] = int(expire.timestamp())
    
    header = {"alg": "HS256", "typ": "JWT"}
    
    # base64url encoding without trailing '=' padding
    def b64url_encode(data_bytes: bytes) -> str:
        return base64.urlsafe_b64encode(data_bytes).decode().rstrip("=")

    header_segment = b64url_encode(json.dumps(header).encode())
    payload_segment = b64url_encode(json.dumps(payload).encode())
    
    signing_input = f"{header_segment}.{payload_segment}"
    signature = hmac.new(SECRET_KEY.encode(), signing_input.encode(), hashlib.sha256).digest()
    signature_segment = b64url_encode(signature)
    
    return f"{signing_input}.{signature_segment}"

def decode_access_token(token: str) -> Optional[dict]:
    """Decodes, verifies the HMAC signature, and confirms validity/expiration of the token claims."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
            
        header_segment, payload_segment, signature_segment = parts
        
        # Verify HMAC signature
        signing_input = f"{header_segment}.{payload_segment}"
        
        def b64url_decode(segment: str) -> bytes:
            # Re-add padding characters if required by Python standard base64 decoder
            rem = len(segment) % 4
            if rem > 0:
                segment += "=" * (4 - rem)
            return base64.urlsafe_b64decode(segment)
            
        sig = b64url_decode(signature_segment)
        expected_sig = hmac.new(SECRET_KEY.encode(), signing_input.encode(), hashlib.sha256).digest()
        
        if not hmac.compare_digest(sig, expected_sig):
            logger.warning("Token verification failed: Signature mismatch.")
            return None
            
        payload = json.loads(b64url_decode(payload_segment).decode())
        
        # Check expiration timestamp
        exp = payload.get("exp")
        if exp and exp < int(datetime.utcnow().timestamp()):
            logger.warning("Token verification failed: Token has expired.")
            return None
            
        return payload
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        return None

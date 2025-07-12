import json
from datetime import datetime
from pathlib import Path

FINGERPRINT_FILE = Path("device_fingerprints.json")

def load_fingerprints():
    """Load device fingerprint data"""
    if FINGERPRINT_FILE.exists():
        try:
            with open(FINGERPRINT_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_fingerprints(data):
    """Save device fingerprint data"""
    with open(FINGERPRINT_FILE, "w") as f:
        json.dump(data, f, indent=2)

def analyze_device_token(device_token: str):
    """
    Analyze device token to detect potential abuse patterns
    Returns the base identifier to use for rate limiting
    """
    if not device_token:
        return device_token
    
    # Split fingerprint and localStorage token
    parts = device_token.split('-')
    if len(parts) >= 2:
        fingerprint = parts[0]
        storage_token = '-'.join(parts[1:])
        
        # Load existing fingerprint data
        fingerprints = load_fingerprints()
        
        # Check if this fingerprint has been seen before
        if fingerprint in fingerprints:
            # Use the first storage token we saw for this fingerprint
            # This prevents creating new identities with same device
            existing_tokens = fingerprints[fingerprint]
            if storage_token not in existing_tokens:
                existing_tokens.append(storage_token)
                save_fingerprints(fingerprints)
            
            # Use fingerprint as the rate limiting key
            return fingerprint
        else:
            # New fingerprint, record it
            fingerprints[fingerprint] = [storage_token]
            save_fingerprints(fingerprints)
            return fingerprint
    
    # Fallback to original token if parsing fails
    return device_token

def get_device_identifier(device_token: str, fallback_ip: str):
    """
    Get the identifier to use for rate limiting and user identification
    """
    if device_token:
        return analyze_device_token(device_token)
    else:
        # Fallback to IP if no device token
        return fallback_ip

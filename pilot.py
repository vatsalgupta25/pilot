import re
import string
from datetime import datetime
from db import save_url_mapping

import os
import json

# Constants for ID Generation
CUSTOM_EPOCH = datetime(2024, 1, 1)
MACHINE_ID = 1  # 6-bit limit (0-63)

# Global state for the counter
_state_loaded = False
_last_day = -1
_daily_counter = 0
STATE_FILE = ".pilot_state.json"

BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase

def _load_state():
    global _last_day, _daily_counter, _state_loaded
    if not _state_loaded:
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    data = json.load(f)
                    _last_day = data.get("last_day", -1)
                    _daily_counter = data.get("daily_counter", 0)
            except json.JSONDecodeError:
                pass
        _state_loaded = True

def _save_state():
    with open(STATE_FILE, "w") as f:
        json.dump({"last_day": _last_day, "daily_counter": _daily_counter}, f)

def base62_encode(num: int) -> str:
    """Encodes a given integer to a Base62 string."""
    if num == 0:
        return BASE62_ALPHABET[0]
    
    base62 = []
    base = len(BASE62_ALPHABET)
    while num > 0:
        num, rem = divmod(num, base)
        base62.append(BASE62_ALPHABET[rem])
    
    return ''.join(reversed(base62))

def generate_unique_integer() -> int:
    """
    Generates a unique 41-bit integer using:
    - 15 bits: Days since custom epoch
    - 6 bits: Machine ID
    - 20 bits: Daily counter
    """
    global _last_day, _daily_counter
    _load_state()
    
    today = datetime.now()
    days_since_epoch = (today - CUSTOM_EPOCH).days
    
    # Reset counter if it's a new day
    if days_since_epoch != _last_day:
        _last_day = days_since_epoch
        _daily_counter = 0
    else:
        _daily_counter += 1
        if _daily_counter > 1048575:  # 2^20 - 1
            raise OverflowError("Daily counter exceeded 20 bits limit (1 million writes/day/machine).")
            
    _save_state()
            
    # Shift bits into their dedicated slots
    date_part = days_since_epoch << 26  # 20 + 6
    machine_part = MACHINE_ID << 20
    
    # Combine using Bitwise OR
    return date_part | machine_part | _daily_counter

def pilot(url: str) -> str:
    """
    Core function to process the incoming URL.
    Uses Snowflake-like 41-bit ID generation + Base62 encoding.
    """
    # Cap URL length at 100 characters excluding the protocol
    url_without_protocol = re.sub(r'^[a-zA-Z]+://', '', url)
    if len(url_without_protocol) > 100:
        raise ValueError("URL exceeds the maximum allowed length of 100 characters (excluding protocol).")

    # 1. Generate unique ID
    unique_id = generate_unique_integer()
    
    # 2. Base62 Encode
    encoded_str = base62_encode(unique_id)
    
    # Generate the short URL (using a dummy domain for now)
    short_url = f"https://pi.lot/{encoded_str}"
    
    # If the original URL is shorter than or equal to the short URL, just return the original
    if len(url) <= len(short_url):
        return url
        
    # Save mapping to the database
    save_url_mapping(url, encoded_str)
    
    return short_url

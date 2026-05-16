import base64
from db import save_url_mapping

def pilot(url: str) -> str:
    """
    Core function to process the incoming URL.
    Logic to be expanded later.
    Currently encodes the URL into a base32 string to form a short URL.
    """
    # Convert the URL string to bytes
    url_bytes = url.encode('utf-8')
    
    # Encode the bytes into base32
    encoded_bytes = base64.b32encode(url_bytes)
    
    # Convert back to string and remove base32 padding '=' characters
    encoded_str = encoded_bytes.decode('utf-8').rstrip('=')
    
    # Generate the short URL (using a dummy domain for now)
    short_url = f"https://pi.lot/{encoded_str}"
    
    # Save mapping to the database
    save_url_mapping(url, encoded_str)
    
    return short_url

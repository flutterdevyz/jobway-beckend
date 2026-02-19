from typing import Optional
from app.core.config import settings
from app.core.context import get_base_url

def get_full_url(path: Optional[str]) -> Optional[str]:
    """
    Converts a relative image/file path to a full absolute HTTP URL.
    Args:
        path: The relative path or filename (e.g., 'avatar.jpg' or 'uploads/avatar.jpg').
    Returns:
        The full absolute URL (e.g., 'http://localhost:8080/uploads/avatar.jpg') or None.
    """
    if not path:
        return None
    
    path_str = str(path).strip()
    
    # Handle 'None' as a string or empty values
    if path_str.lower() == "none" or not path_str:
        return None
        
    # If it's already an absolute URL or data URI, return as is
    if path_str.startswith(("http://", "https://", "data:")):
        return path_str
        
    # Get base URL from request context or fallback to settings
    base_url = get_base_url() or settings.BASE_URL
    base_url = base_url.rstrip("/")
    
    # Ensure the path starts with /uploads/ if it's just a filename
    clean_path = path_str.lstrip("/")
    if not clean_path.startswith("uploads/"):
        clean_path = f"uploads/{clean_path}"
        
    return f"{base_url}/{clean_path}"

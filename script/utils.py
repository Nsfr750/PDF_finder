"""Utility functions for PDF Duplicate Finder."""
import os
from typing import Any, Dict, Union, Optional

# Import language manager
from lang.language_manager import LanguageManager

def get_file_path(file_info: Union[Dict[str, Any], object], path_key: str = 'file_path') -> Optional[str]:
    """
    Get the file path from a file info object or dictionary.
    
    Args:
        file_info: Either a dictionary with file info or an object with attributes
        path_key: The key to use when file_info is a dictionary (default: 'file_path')
        
    Returns:
        The file path if found, None otherwise
    """
    if file_info is None:
        return None
        
    # Handle dictionary case
    if isinstance(file_info, dict):
        # Try multiple possible keys
        for key in [path_key, 'path', 'filepath', 'file']:
            if key in file_info and file_info[key]:
                return str(file_info[key])
        return None
        
    # Handle object case
    for attr in ['file_path', 'path', 'filepath', 'file']:
        if hasattr(file_info, attr) and getattr(file_info, attr):
            return str(getattr(file_info, attr))
            
    return None


def get_file_info_dict(file_info: Union[Dict[str, Any], object]) -> Dict[str, Any]:
    """
    Convert a file info object to a dictionary with consistent keys.
    
    Args:
        file_info: Either a dictionary with file info or an object with attributes
        
    Returns:
        A dictionary with consistent keys
    """
    if file_info is None:
        return {}
        
    # If it's already a dictionary, ensure it has the right keys
    if isinstance(file_info, dict):
        result = dict(file_info)  # Create a copy
        # Ensure path is set from any of the possible keys
        for key in ['path', 'filepath', 'file']:
            if key in result and key != 'path':
                result['path'] = result[key]
                break
        return result
        
    # Convert object to dictionary
    result = {}
    for attr in ['file_path', 'path', 'filepath', 'file']:
        if hasattr(file_info, attr):
            result[attr] = getattr(file_info, attr)
            if attr != 'path':
                result['path'] = result[attr]
                
    return result

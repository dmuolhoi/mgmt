"""
Data storage module for the School Management System
"""
import os
import json
from typing import Dict, Any, Optional, List
from utils.constants import DATA_DIR

def initialize_data_store() -> None:
    """
    Initialize the data store by creating necessary directories and files.
    """
    # Create data directory if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Create each data file if it doesn't exist
    data_files = [
        'users.json',
        'students.json',
        'teachers.json',
        'staff.json',
        'parents.json',
        'courses.json',
        'assignments.json',
        'attendance.json',
        'events.json',
        'announcements.json',
        'fees.json',
        'grades.json',
        'messages.json'
    ]
    
    for file_name in data_files:
        file_path = os.path.join(DATA_DIR, file_name)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump({}, f)

def get_data(data_type: str) -> Dict[str, Any]:
    """
    Get data from storage.
    
    Args:
        data_type: Type of data to get (e.g., 'users', 'students')
    
    Returns:
        Dictionary containing the requested data
    """
    file_path = os.path.join(DATA_DIR, f"{data_type}.json")
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is empty/invalid, return empty dict
        return {}

def save_data(data_type: str, data: Dict[str, Any]) -> None:
    """
    Save data to storage.
    
    Args:
        data_type: Type of data to save (e.g., 'users', 'students')
        data: Dictionary containing the data to save
    """
    file_path = os.path.join(DATA_DIR, f"{data_type}.json")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def add_item(data_type: str, item_id: str, item_data: Dict[str, Any]) -> None:
    """
    Add a new item to a collection.
    
    Args:
        data_type: Type of data to update (e.g., 'students')
        item_id: ID for the item
        item_data: Data for the item
    """
    data = get_data(data_type)
    data[item_id] = item_data
    save_data(data_type, data)

def update_item(data_type: str, item_id: str, 
                update_data: Dict[str, Any]) -> bool:
    """
    Update an existing item in a collection.
    
    Args:
        data_type: Type of data to update (e.g., 'students')
        item_id: ID of the item to update
        update_data: New data to update
    
    Returns:
        True if successful, False if item not found
    """
    data = get_data(data_type)
    
    if item_id in data:
        data[item_id].update(update_data)
        save_data(data_type, data)
        return True
    
    return False

def delete_item(data_type: str, item_id: str) -> bool:
    """
    Delete an item from a collection.
    
    Args:
        data_type: Type of data to update (e.g., 'students')
        item_id: ID of the item to delete
    
    Returns:
        True if successful, False if item not found
    """
    data = get_data(data_type)
    
    if item_id in data:
        del data[item_id]
        save_data(data_type, data)
        return True
    
    return False

def get_item(data_type: str, item_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific item from a collection.
    
    Args:
        data_type: Type of data (e.g., 'students')
        item_id: ID of the item to get
    
    Returns:
        Item data if found, None otherwise
    """
    data = get_data(data_type)
    return data.get(item_id)

def get_filtered_items(data_type: str, 
                       filter_func) -> Dict[str, Dict[str, Any]]:
    """
    Get items filtered by a function.
    
    Args:
        data_type: Type of data (e.g., 'students')
        filter_func: Function that takes (id, item) and returns bool
    
    Returns:
        Dictionary of filtered items
    """
    data = get_data(data_type)
    return {id_: item for id_, item in data.items() if filter_func(id_, item)}

def get_all_items(data_type: str) -> Dict[str, Dict[str, Any]]:
    """
    Get all items from a collection.
    
    Args:
        data_type: Type of data (e.g., 'students')
    
    Returns:
        Dictionary of all items
    """
    return get_data(data_type)

def get_items_list(data_type: str) -> List[Dict[str, Any]]:
    """
    Get all items as a list.
    
    Args:
        data_type: Type of data (e.g., 'students')
    
    Returns:
        List of all items with id included
    """
    data = get_data(data_type)
    return [
        {**item, "id": id_} 
        for id_, item in data.items()
    ]
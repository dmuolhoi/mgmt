"""
Event service for the School Management System
"""
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from storage.datastore import get_data, save_data, add_item

def create_event(username: str, title: str, description: str, event_type: str,
                 start_date: str, start_time: str, end_date: str, end_time: str,
                 location: str, visibility: List[str]) -> Tuple[bool, str]:
    """
    Create a new event.
    
    Args:
        username: Username of the user creating the event
        title: Title of the event
        description: Description of the event
        event_type: Type of event (holiday, exam, meeting, etc.)
        start_date: Start date of the event (YYYY-MM-DD)
        start_time: Start time of the event (HH:MM)
        end_date: End date of the event (YYYY-MM-DD)
        end_time: End time of the event (HH:MM)
        location: Location of the event
        visibility: List of roles that can see the event
    
    Returns:
        Tuple of (success, message)
    """
    # Validate inputs
    if not title:
        return False, "❌ Event title is required."
    
    # Validate dates
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return False, "❌ Invalid date format. Use YYYY-MM-DD."
    
    # Validate times
    try:
        datetime.strptime(start_time, "%H:%M")
        datetime.strptime(end_time, "%H:%M")
    except ValueError:
        return False, "❌ Invalid time format. Use HH:MM."
    
    # Create event
    events = get_data('events')
    event_id = f"EVT{len(events) + 1:04d}"
    
    events[event_id] = {
        "title": title,
        "description": description,
        "event_type": event_type,
        "start_date": start_date,
        "start_time": start_time,
        "end_date": end_date,
        "end_time": end_time,
        "location": location,
        "visibility": visibility,
        "created_at": datetime.now().isoformat(),
        "created_by": username,
        "is_cancelled": False
    }
    
    save_data('events', events)
    
    return True, "✅ Event created successfully."

def list_events(filter_func=None) -> List[Dict[str, Any]]:
    """
    List events, optionally filtered by a function.
    
    Args:
        filter_func: Optional function to filter events
    
    Returns:
        List of event dictionaries with IDs
    """
    events = get_data('events')
    
    # Convert to list with ID included
    event_list = []
    for event_id, event in events.items():
        if not event.get("is_cancelled", False):  # Skip cancelled events
            if filter_func is None or filter_func(event):
                event_list.append({**event, "id": event_id})
    
    return event_list

def get_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
    """
    Get an event by its ID.
    
    Args:
        event_id: ID of the event
    
    Returns:
        Event dictionary or None if not found
    """
    events = get_data('events')
    event = events.get(event_id)
    
    if event:
        return {**event, "id": event_id}
    
    return None

def update_event(event_id: str, update_data: Dict[str, Any], username: str) -> Tuple[bool, str]:
    """
    Update an existing event.
    
    Args:
        event_id: ID of the event to update
        update_data: Data to update in the event
        username: Username of the user making the update
    
    Returns:
        Tuple of (success, message)
    """
    events = get_data('events')
    
    if event_id not in events:
        return False, "❌ Event not found."
    
    # Update the event
    events[event_id].update(update_data)
    events[event_id]["modified_at"] = datetime.now().isoformat()
    events[event_id]["modified_by"] = username
    
    save_data('events', events)
    
    return True, "✅ Event updated successfully."

def cancel_event(event_id: str, username: str) -> Tuple[bool, str]:
    """
    Cancel an event.
    
    Args:
        event_id: ID of the event to cancel
        username: Username of the user cancelling the event
    
    Returns:
        Tuple of (success, message)
    """
    events = get_data('events')
    
    if event_id not in events:
        return False, "❌ Event not found."
    
    # Mark the event as cancelled
    events[event_id]["is_cancelled"] = True
    events[event_id]["cancelled_at"] = datetime.now().isoformat()
    events[event_id]["cancelled_by"] = username
    
    save_data('events', events)
    
    return True, "✅ Event cancelled successfully."

def get_upcoming_events(role: str = None, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get upcoming events for a specific role.
    
    Args:
        role: Role to filter events for
        limit: Maximum number of events to return
    
    Returns:
        List of upcoming event dictionaries
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    def filter_func(event):
        # Check if event is in the future
        if event.get("start_date", "") < today:
            return False
        
        # Check if event is visible to the role
        visibility = event.get("visibility", [])
        if not visibility or "all" in visibility:
            return True
        
        return role in visibility
    
    events = list_events(filter_func)
    
    # Sort by start date
    events.sort(key=lambda x: (x.get("start_date", ""), x.get("start_time", "")))
    
    # Return limited number of events
    return events[:limit]
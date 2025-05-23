"""
Staff service for the School Management System
"""
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from storage.datastore import get_data, save_data
from utils.constants import USER_ROLES
from services.user_service import create_user
from utils.helpers import generate_id

def add_staff(admin_username: str, username: str, password: str,
             first_name: str, last_name: str, email: str, phone: str,
             position: str, department: str) -> Tuple[bool, str]:
    """
    Add a new staff member.
    
    Args:
        admin_username: Username of the admin adding the staff member
        username: Username for the staff member
        password: Password for the staff member
        first_name: First name of the staff member
        last_name: Last name of the staff member
        email: Email of the staff member
        phone: Phone number of the staff member
        position: Position of the staff member
        department: Department of the staff member
    
    Returns:
        Tuple of (success, message)
    """
    # Create user account first
    success, message, user_id = create_user(
        username, 
        password, 
        USER_ROLES.STAFF, 
        first_name, 
        last_name, 
        email, 
        phone, 
        admin_username
    )
    
    if not success:
        return False, message
    
    # Generate staff ID
    staff_id = generate_id("STF")
    
    # Update user record with proper ID
    users = get_data('users')
    users[username]["id"] = staff_id
    save_data('users', users)
    
    # Create staff record
    staff = get_data('staff')
    staff[staff_id] = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "position": position,
        "department": department,
        "hire_date": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
        "created_by": admin_username
    }
    
    save_data('staff', staff)
    
    return True, f"✅ Staff member '{first_name} {last_name}' added successfully."

def get_staff_details(staff_id: str) -> Optional[Dict[str, Any]]:
    """
    Get details for a specific staff member.
    
    Args:
        staff_id: ID of the staff member
    
    Returns:
        Staff details if found, None otherwise
    """
    staff = get_data('staff')
    staff_member = staff.get(staff_id)
    
    if staff_member:
        return {**staff_member, "id": staff_id}
    
    return None

def update_staff(staff_id: str, update_data: Dict[str, Any], 
                updater_username: str) -> Tuple[bool, str]:
    """
    Update a staff member's information.
    
    Args:
        staff_id: ID of the staff member to update
        update_data: Data to update
        updater_username: Username of the user making the update
    
    Returns:
        Tuple of (success, message)
    """
    staff = get_data('staff')
    
    if staff_id not in staff:
        return False, f"❌ Staff member with ID '{staff_id}' not found."
    
    # Update staff data
    for key, value in update_data.items():
        staff[staff_id][key] = value
    
    # Update modification metadata
    staff[staff_id]["modified_at"] = datetime.now().isoformat()
    staff[staff_id]["modified_by"] = updater_username
    
    save_data('staff', staff)
    
    # If username is in update_data, update user record as well
    if "username" in update_data:
        users = get_data('users')
        old_username = None
        
        # Find the corresponding user
        for username, user in users.items():
            if user.get("id") == staff_id:
                old_username = username
                break
        
        if old_username and old_username != update_data["username"]:
            # Create a new entry with updated username
            new_username = update_data["username"]
            users[new_username] = users[old_username]
            users[new_username]["username"] = new_username
            users[new_username]["modified_at"] = datetime.now().isoformat()
            users[new_username]["modified_by"] = updater_username
            
            # Remove old entry
            del users[old_username]
            
            save_data('users', users)
    
    return True, f"✅ Staff member information updated successfully."

def assign_duty_to_staff(staff_id: str, duty: Dict[str, Any], 
                        assigning_username: str) -> Tuple[bool, str]:
    """
    Assign a duty to a staff member.
    
    Args:
        staff_id: ID of the staff member
        duty: Duty information (description, date, time, etc.)
        assigning_username: Username of the user making the assignment
    
    Returns:
        Tuple of (success, message)
    """
    staff = get_data('staff')
    
    if staff_id not in staff:
        return False, f"❌ Staff member with ID '{staff_id}' not found."
    
    # Add duty to staff member's duties
    if "duties" not in staff[staff_id]:
        staff[staff_id]["duties"] = []
    
    # Add duty ID and assignment metadata
    duty_id = f"DTY{len(staff[staff_id]['duties']) + 1:04d}"
    duty["id"] = duty_id
    duty["assigned_at"] = datetime.now().isoformat()
    duty["assigned_by"] = assigning_username
    duty["status"] = "assigned"
    
    staff[staff_id]["duties"].append(duty)
    staff[staff_id]["modified_at"] = datetime.now().isoformat()
    staff[staff_id]["modified_by"] = assigning_username
    
    save_data('staff', staff)
    
    staff_name = f"{staff[staff_id].get('first_name', '')} {staff[staff_id].get('last_name', '')}".strip()
    
    return True, f"✅ Duty assigned to {staff_name} successfully."

def get_staff_by_department(department: str) -> List[Dict[str, Any]]:
    """
    Get a list of staff members in a specific department.
    
    Args:
        department: Department to filter by
    
    Returns:
        List of staff dictionaries
    """
    staff = get_data('staff')
    
    return [
        {**staff_member, "id": staff_id}
        for staff_id, staff_member in staff.items()
        if staff_member.get("department") == department
    ]

def get_staff_by_position(position: str) -> List[Dict[str, Any]]:
    """
    Get a list of staff members with a specific position.
    
    Args:
        position: Position to filter by
    
    Returns:
        List of staff dictionaries
    """
    staff = get_data('staff')
    
    return [
        {**staff_member, "id": staff_id}
        for staff_id, staff_member in staff.items()
        if staff_member.get("position") == position
    ]

def log_facility_issue(staff_id: str, issue: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Log a facility issue.
    
    Args:
        staff_id: ID of the staff member logging the issue
        issue: Issue information (description, location, priority, etc.)
    
    Returns:
        Tuple of (success, message)
    """
    staff = get_data('staff')
    
    if staff_id not in staff:
        return False, f"❌ Staff member with ID '{staff_id}' not found."
    
    # Get facility issues data
    facility_issues = get_data('facility_issues')
    
    # Generate issue ID
    issue_id = f"ISS{len(facility_issues) + 1:04d}"
    
    # Add metadata to issue
    issue["id"] = issue_id
    issue["reported_by"] = staff_id
    issue["reported_at"] = datetime.now().isoformat()
    issue["status"] = "reported"
    
    # Save the issue
    facility_issues[issue_id] = issue
    save_data('facility_issues', facility_issues)
    
    return True, f"✅ Facility issue logged successfully. Issue ID: {issue_id}"

def request_leave(staff_id: str, leave_request: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Submit a leave request.
    
    Args:
        staff_id: ID of the staff member requesting leave
        leave_request: Leave request information (start date, end date, reason, etc.)
    
    Returns:
        Tuple of (success, message)
    """
    staff = get_data('staff')
    
    if staff_id not in staff:
        return False, f"❌ Staff member with ID '{staff_id}' not found."
    
    # Get leave requests data
    leave_requests = get_data('leave_requests')
    
    # Generate leave request ID
    request_id = f"LVR{len(leave_requests) + 1:04d}"
    
    # Add metadata to leave request
    leave_request["id"] = request_id
    leave_request["requested_by"] = staff_id
    leave_request["requested_at"] = datetime.now().isoformat()
    leave_request["status"] = "pending"
    
    # Save the leave request
    leave_requests[request_id] = leave_request
    save_data('leave_requests', leave_requests)
    
    return True, f"✅ Leave request submitted successfully. Request ID: {request_id}"
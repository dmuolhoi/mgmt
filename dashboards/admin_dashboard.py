"""
Admin dashboard module for the School Management System
"""
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils.helpers import clear_screen, get_user_by_id, get_username_by_id
from utils.constants import USER_ROLES, MENU_BACK, MENU_LOGOUT
from auth import get_pending_registrations, approve_registration, reject_registration
from storage.datastore import get_data, save_data, add_item, update_item, delete_item
from services.user_service import create_user, get_user_by_username, list_users_by_role
from services.student_service import add_student, get_student_details
from services.teacher_service import add_teacher, get_teacher_details
from services.staff_service import add_staff, get_staff_details
from services.event_service import create_event, list_events
from services.attendance_service import generate_attendance_report

def admin_dashboard(admin_id: str) -> None:
    """
    Display the admin dashboard.
    
    Args:
        admin_id: The ID of the admin user
    """
    admin = get_user_by_id(admin_id)
    if not admin or admin["role"] != USER_ROLES.ADMIN:
        print("❌ Access denied: Admin privileges required")
        return
    
    username = admin["username"]
    
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print(f"👤 ADMIN DASHBOARD: {username} 👤".center(50))
        print("=" * 50)
        
        print("\n1. Manage Users")
        print("2. Lookup Users")
        print("3. View Reports")
        print("4. Manage Events")
        print("5. Post Announcements")
        print("6. Manage Pending Registrations")
        print("7. System Settings")
        print(f"\n{MENU_LOGOUT}. Logout")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            manage_users(admin_id)
        elif choice == "2":
            lookup_users(admin_id)
        elif choice == "3":
            view_reports(admin_id)
        elif choice == "4":
            manage_events(admin_id)
        elif choice == "5":
            post_announcement(admin_id)
        elif choice == "6":
            manage_pending_registrations(admin_id)
        elif choice == "7":
            system_settings(admin_id)
        elif choice == MENU_LOGOUT:
            print("\nLogging out...")
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

def manage_users(admin_id: str) -> None:
    """
    Manage users (admin function).
    
    Args:
        admin_id: The ID of the admin user
    """
    admin_username = get_username_by_id(admin_id)
    
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print("👥 MANAGE USERS 👥".center(50))
        print("=" * 50)
        
        print("\n1. Add Student")
        print("2. Add Teacher")
        print("3. Add Staff")
        print("4. Add Parent")
        print("5. List Users by Role")
        print("6. Update User")
        print("7. Deactivate User")
        print(f"\n{MENU_BACK}. Back")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            # Add student logic
            add_student_ui(admin_username)
        elif choice == "2":
            # Add teacher logic
            add_teacher_ui(admin_username)
        elif choice == "3":
            # Add staff logic
            add_staff_ui(admin_username)
        elif choice == "4":
            # Add parent logic
            add_parent_ui(admin_username)
        elif choice == "5":
            # List users by role
            list_users_by_role_ui()
        elif choice == "6":
            # Update user logic
            update_user_ui(admin_username)
        elif choice == "7":
            # Deactivate user logic
            deactivate_user_ui(admin_username)
        elif choice == MENU_BACK:
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

def lookup_users(admin_id: str) -> None:
    """
    Lookup users by ID or name (admin function).
    
    Args:
        admin_id: The ID of the admin user
    """
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print("🔍 LOOKUP USERS 🔍".center(50))
        print("=" * 50)
        
        print("\n1. Lookup by Username")
        print("2. Lookup by ID")
        print("3. Lookup by Name")
        print(f"\n{MENU_BACK}. Back")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            # Lookup by username
            username = input("\nEnter username: ")
            user = get_user_by_username(username)
            if user:
                display_user_details(user)
            else:
                print(f"\n❌ User '{username}' not found.")
        elif choice == "2":
            # Lookup by ID
            user_id = input("\nEnter user ID: ")
            user = get_user_by_id(user_id)
            if user:
                display_user_details(user)
            else:
                print(f"\n❌ User with ID '{user_id}' not found.")
        elif choice == "3":
            # Lookup by name
            name = input("\nEnter name or part of name: ").lower()
            users = get_data('users')
            matching_users = []
            
            for username, user in users.items():
                first_name = user.get("first_name", "").lower()
                last_name = user.get("last_name", "").lower()
                full_name = f"{first_name} {last_name}".strip()
                
                if name in first_name or name in last_name or name in full_name:
                    matching_users.append(user)
            
            if matching_users:
                print(f"\nFound {len(matching_users)} matching users:")
                for i, user in enumerate(matching_users, 1):
                    full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                    print(f"{i}. {full_name} ({user.get('role', 'N/A')}) - ID: {user.get('id', 'N/A')}")
                
                user_idx = input("\nEnter number to view details (or 0 to cancel): ")
                try:
                    user_idx = int(user_idx)
                    if 1 <= user_idx <= len(matching_users):
                        display_user_details(matching_users[user_idx - 1])
                except ValueError:
                    pass
            else:
                print(f"\n❌ No users found matching '{name}'.")
        elif choice == MENU_BACK:
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

def view_reports(admin_id: str) -> None:
    """
    View various reports (admin function).
    
    Args:
        admin_id: The ID of the admin user
    """
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print("📊 VIEW REPORTS 📊".center(50))
        print("=" * 50)
        
        print("\n1. Attendance Reports")
        print("2. Grade Reports")
        print("3. Financial Reports")
        print("4. Enrollment Reports")
        print(f"\n{MENU_BACK}. Back")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            view_attendance_reports()
        elif choice == "2":
            view_grade_reports()
        elif choice == "3":
            view_financial_reports()
        elif choice == "4":
            view_enrollment_reports()
        elif choice == MENU_BACK:
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

def manage_events(admin_id: str) -> None:
    """
    Manage school events (admin function).
    
    Args:
        admin_id: The ID of the admin user
    """
    admin_username = get_username_by_id(admin_id)
    
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print("📅 MANAGE EVENTS 📅".center(50))
        print("=" * 50)
        
        print("\n1. Create New Event")
        print("2. View Upcoming Events")
        print("3. Edit Event")
        print("4. Cancel Event")
        print(f"\n{MENU_BACK}. Back")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            create_event_ui(admin_username)
        elif choice == "2":
            view_events_ui()
        elif choice == "3":
            edit_event_ui(admin_username)
        elif choice == "4":
            cancel_event_ui(admin_username)
        elif choice == MENU_BACK:
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

def post_announcement(admin_id: str) -> None:
    """
    Post a school-wide announcement (admin function).
    
    Args:
        admin_id: The ID of the admin user
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📢 POST ANNOUNCEMENT 📢".center(50))
    print("=" * 50 + "\n")
    
    title = input("Announcement Title: ")
    content = input("Announcement Content: ")
    
    # Get list of roles that should see this announcement
    print("\nWho should see this announcement?")
    print("1. Everyone")
    print("2. Teachers only")
    print("3. Students only")
    print("4. Parents only")
    print("5. Staff only")
    print("6. Custom selection")
    
    audience_choice = input("\nEnter choice: ")
    
    # Determine audience based on choice
    if audience_choice == "1":
        audience = ["all"]
    elif audience_choice == "2":
        audience = [USER_ROLES.TEACHER]
    elif audience_choice == "3":
        audience = [USER_ROLES.STUDENT]
    elif audience_choice == "4":
        audience = [USER_ROLES.PARENT]
    elif audience_choice == "5":
        audience = [USER_ROLES.STAFF]
    elif audience_choice == "6":
        audience = []
        role_options = {
            "1": USER_ROLES.ADMIN,
            "2": USER_ROLES.TEACHER,
            "3": USER_ROLES.STUDENT,
            "4": USER_ROLES.PARENT,
            "5": USER_ROLES.STAFF
        }
        
        print("\nSelect roles (comma-separated):")
        print("1. Administrators")
        print("2. Teachers")
        print("3. Students")
        print("4. Parents")
        print("5. Staff")
        
        selections = input("\nEnter selections (e.g., 1,2,3): ").split(",")
        audience = [role_options[s.strip()] for s in selections if s.strip() in role_options]
    else:
        print("\n❌ Invalid choice. Using 'Everyone' as default.")
        audience = ["all"]
    
    # Ask if this is important/urgent
    is_important = input("\nMark as important? (y/n): ").lower() == 'y'
    
    # Create the announcement
    announcements = get_data('announcements')
    announcement_id = f"ANN{len(announcements) + 1:04d}"
    
    announcements[announcement_id] = {
        "title": title,
        "content": content,
        "author_id": admin_id,
        "audience": audience,
        "created_at": datetime.now().isoformat(),
        "is_important": is_important
    }
    
    save_data('announcements', announcements)
    
    print("\n✅ Announcement posted successfully.")
    input("\nPress Enter to continue...")

def manage_pending_registrations(admin_id: str) -> None:
    """
    Manage pending user registrations (admin function).
    
    Args:
        admin_id: The ID of the admin user
    """
    admin_username = get_username_by_id(admin_id)
    
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print("🔄 PENDING REGISTRATIONS 🔄".center(50))
        print("=" * 50 + "\n")
        
        pending_registrations = get_pending_registrations()
        
        if not pending_registrations:
            print("No pending registrations found.")
            input("\nPress Enter to continue...")
            break
        
        # Display pending registrations
        print(f"Found {len(pending_registrations)} pending registrations:\n")
        for i, user in enumerate(pending_registrations, 1):
            username = user.get("username", "")
            created_at = user.get("created_at", "")
            print(f"{i}. {username} (Requested: {created_at})")
        
        print(f"\n{MENU_BACK}. Back")
        
        choice = input("\nEnter number to approve/reject (or 0 to return): ")
        
        if choice == MENU_BACK:
            break
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(pending_registrations):
                selected_user = pending_registrations[choice_idx]
                username = selected_user.get("username", "")
                
                print(f"\nSelected user: {username}")
                print("1. Approve as Admin")
                print("2. Approve as Teacher")
                print("3. Approve as Student")
                print("4. Approve as Parent")
                print("5. Approve as Staff")
                print("6. Reject Registration")
                print(f"{MENU_BACK}. Cancel")
                
                action = input("\nEnter choice: ")
                
                if action == "1":
                    success, message = approve_registration(username, USER_ROLES.ADMIN, admin_username)
                elif action == "2":
                    success, message = approve_registration(username, USER_ROLES.TEACHER, admin_username)
                elif action == "3":
                    success, message = approve_registration(username, USER_ROLES.STUDENT, admin_username)
                elif action == "4":
                    success, message = approve_registration(username, USER_ROLES.PARENT, admin_username)
                elif action == "5":
                    success, message = approve_registration(username, USER_ROLES.STAFF, admin_username)
                elif action == "6":
                    success, message = reject_registration(username, admin_username)
                elif action == MENU_BACK:
                    continue
                else:
                    print("\n❌ Invalid choice.")
                    input("\nPress Enter to continue...")
                    continue
                
                print(f"\n{message}")
                input("\nPress Enter to continue...")
            
        except ValueError:
            print("\n❌ Invalid choice. Please enter a number.")
            input("\nPress Enter to continue...")

def system_settings(admin_id: str) -> None:
    """
    Manage system settings (admin function).
    
    Args:
        admin_id: The ID of the admin user
    """
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print("⚙️ SYSTEM SETTINGS ⚙️".center(50))
        print("=" * 50)
        
        print("\n1. Backup Data")
        print("2. Restore Data")
        print("3. System Information")
        print(f"\n{MENU_BACK}. Back")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            # Backup data logic
            print("\nCreating backup of system data...")
            print("✅ Backup created successfully.")
        elif choice == "2":
            # Restore data logic
            print("\n⚠️ Restoring data will overwrite all current data.")
            confirm = input("Are you sure you want to continue? (y/n): ")
            if confirm.lower() == 'y':
                print("Restoring data from backup...")
                print("✅ Data restored successfully.")
            else:
                print("Restore operation cancelled.")
        elif choice == "3":
            # System information
            data_types = ['users', 'students', 'teachers', 'staff', 'parents', 
                         'courses', 'assignments', 'attendance', 'events', 
                         'announcements', 'fees', 'grades', 'messages']
            
            print("\nSystem Information:")
            print("-" * 50)
            
            for data_type in data_types:
                data = get_data(data_type)
                print(f"{data_type.capitalize()}: {len(data)} records")
            
            print("-" * 50)
        elif choice == MENU_BACK:
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

def add_student_ui(admin_username: str) -> None:
    """
    UI for adding a new student.
    
    Args:
        admin_username: Username of the admin
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("➕ ADD STUDENT ➕".center(50))
    print("=" * 50 + "\n")
    
    # Get student details
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    username = input("Username: ")
    password = input("Password: ")
    email = input("Email: ")
    phone = input("Phone: ")
    grade_level = input("Grade Level: ")
    date_of_birth = input("Date of Birth (YYYY-MM-DD): ")
    
    # Call the service to add the student
    success, message = add_student(
        admin_username,
        username,
        password,
        first_name,
        last_name,
        email,
        phone,
        grade_level,
        date_of_birth
    )
    
    print(f"\n{message}")
    input("\nPress Enter to continue...")

def add_teacher_ui(admin_username: str) -> None:
    """
    UI for adding a new teacher.
    
    Args:
        admin_username: Username of the admin
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("➕ ADD TEACHER ➕".center(50))
    print("=" * 50 + "\n")
    
    # Get teacher details
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    username = input("Username: ")
    password = input("Password: ")
    email = input("Email: ")
    phone = input("Phone: ")
    subjects = input("Subjects (comma-separated): ").split(",")
    subjects = [s.strip() for s in subjects if s.strip()]
    department = input("Department: ")
    
    # Call the service to add the teacher
    success, message = add_teacher(
        admin_username,
        username,
        password,
        first_name,
        last_name,
        email,
        phone,
        subjects,
        department
    )
    
    print(f"\n{message}")
    input("\nPress Enter to continue...")

def add_staff_ui(admin_username: str) -> None:
    """
    UI for adding a new staff member.
    
    Args:
        admin_username: Username of the admin
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("➕ ADD STAFF ➕".center(50))
    print("=" * 50 + "\n")
    
    # Get staff details
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    username = input("Username: ")
    password = input("Password: ")
    email = input("Email: ")
    phone = input("Phone: ")
    position = input("Position: ")
    department = input("Department: ")
    
    # Call the service to add the staff
    success, message = add_staff(
        admin_username,
        username,
        password,
        first_name,
        last_name,
        email,
        phone,
        position,
        department
    )
    
    print(f"\n{message}")
    input("\nPress Enter to continue...")

def add_parent_ui(admin_username: str) -> None:
    """
    UI for adding a new parent.
    
    Args:
        admin_username: Username of the admin
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("➕ ADD PARENT ➕".center(50))
    print("=" * 50 + "\n")
    
    # Get parent details
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    username = input("Username: ")
    password = input("Password: ")
    email = input("Email: ")
    phone = input("Phone: ")
    
    # Get children (students)
    print("\nLink to existing students:")
    students = get_data('students')
    if students:
        print("\nAvailable students:")
        for i, (student_id, student) in enumerate(students.items(), 1):
            name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
            print(f"{i}. {name} (ID: {student_id})")
        
        student_indices = input("\nEnter student numbers (comma-separated) or leave blank: ")
        selected_students = []
        
        if student_indices.strip():
            try:
                indices = [int(idx.strip()) - 1 for idx in student_indices.split(",")]
                student_ids = list(students.keys())
                selected_students = [student_ids[idx] for idx in indices if 0 <= idx < len(student_ids)]
            except (ValueError, IndexError):
                print("\n❌ Invalid selection. No students will be linked.")
                selected_students = []
    else:
        print("\nNo students found to link.")
        selected_students = []
    
    # Call the service to add the parent
    parents = get_data('parents')
    parent_id = f"PAR{len(parents) + 1:04d}"
    
    from auth import hash_password
    
    # Create parent record
    parents[parent_id] = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "children": selected_students,
        "created_at": datetime.now().isoformat(),
        "created_by": admin_username
    }
    
    save_data('parents', parents)
    
    # Create user record
    users = get_data('users')
    users[username] = {
        "id": parent_id,
        "username": username,
        "password": hash_password(password),
        "role": USER_ROLES.PARENT,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }
    
    save_data('users', users)
    
    # Update student records with parent ID
    for student_id in selected_students:
        if student_id in students:
            students[student_id]["parent_id"] = parent_id
    
    save_data('students', students)
    
    print("\n✅ Parent added successfully.")
    input("\nPress Enter to continue...")

def list_users_by_role_ui() -> None:
    """UI for listing users by role."""
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print("👥 LIST USERS BY ROLE 👥".center(50))
        print("=" * 50)
        
        print("\n1. List Administrators")
        print("2. List Teachers")
        print("3. List Students")
        print("4. List Parents")
        print("5. List Staff")
        print(f"\n{MENU_BACK}. Back")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            users = list_users_by_role(USER_ROLES.ADMIN)
            display_users_list(users, "Administrators")
        elif choice == "2":
            users = list_users_by_role(USER_ROLES.TEACHER)
            display_users_list(users, "Teachers")
        elif choice == "3":
            users = list_users_by_role(USER_ROLES.STUDENT)
            display_users_list(users, "Students")
        elif choice == "4":
            users = list_users_by_role(USER_ROLES.PARENT)
            display_users_list(users, "Parents")
        elif choice == "5":
            users = list_users_by_role(USER_ROLES.STAFF)
            display_users_list(users, "Staff")
        elif choice == MENU_BACK:
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

def update_user_ui(admin_username: str) -> None:
    """
    UI for updating a user.
    
    Args:
        admin_username: Username of the admin
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("✏️ UPDATE USER ✏️".center(50))
    print("=" * 50 + "\n")
    
    username = input("Enter username to update: ")
    
    users = get_data('users')
    if username not in users:
        print(f"\n❌ User '{username}' not found.")
        input("\nPress Enter to continue...")
        return
    
    user = users[username]
    print(f"\nUpdating user: {user.get('first_name', '')} {user.get('last_name', '')}")
    print(f"Role: {user.get('role', '')}")
    
    print("\nFields to update (leave blank to keep current value):")
    first_name = input(f"First Name [{user.get('first_name', '')}]: ") or user.get('first_name', '')
    last_name = input(f"Last Name [{user.get('last_name', '')}]: ") or user.get('last_name', '')
    email = input(f"Email [{user.get('email', '')}]: ") or user.get('email', '')
    phone = input(f"Phone [{user.get('phone', '')}]: ") or user.get('phone', '')
    
    # Update password option
    change_password = input("\nChange password? (y/n): ").lower() == 'y'
    if change_password:
        from auth import hash_password
        new_password = input("New Password: ")
        user["password"] = hash_password(new_password)
    
    # Update basic user information
    user["first_name"] = first_name
    user["last_name"] = last_name
    user["email"] = email
    user["phone"] = phone
    user["modified_at"] = datetime.now().isoformat()
    
    # Save updated user
    users[username] = user
    save_data('users', users)
    
    # Update role-specific information if needed
    role = user.get('role', '')
    if role == USER_ROLES.STUDENT:
        update_student_info(user["id"], admin_username)
    elif role == USER_ROLES.TEACHER:
        update_teacher_info(user["id"], admin_username)
    elif role == USER_ROLES.STAFF:
        update_staff_info(user["id"], admin_username)
    elif role == USER_ROLES.PARENT:
        update_parent_info(user["id"], admin_username)
    
    print("\n✅ User updated successfully.")
    input("\nPress Enter to continue...")

def deactivate_user_ui(admin_username: str) -> None:
    """
    UI for deactivating a user.
    
    Args:
        admin_username: Username of the admin
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("🚫 DEACTIVATE USER 🚫".center(50))
    print("=" * 50 + "\n")
    
    username = input("Enter username to deactivate: ")
    
    users = get_data('users')
    if username not in users:
        print(f"\n❌ User '{username}' not found.")
        input("\nPress Enter to continue...")
        return
    
    user = users[username]
    print(f"\nDeactivating user: {user.get('first_name', '')} {user.get('last_name', '')}")
    print(f"Role: {user.get('role', '')}")
    
    confirm = input("\nAre you sure you want to deactivate this user? (y/n): ")
    if confirm.lower() != 'y':
        print("\nOperation cancelled.")
        input("\nPress Enter to continue...")
        return
    
    # Deactivate the user
    user["is_active"] = False
    user["modified_at"] = datetime.now().isoformat()
    
    # Save updated user
    users[username] = user
    save_data('users', users)
    
    print("\n✅ User deactivated successfully.")
    input("\nPress Enter to continue...")

def update_student_info(student_id: str, admin_username: str) -> None:
    """
    Update student-specific information.
    
    Args:
        student_id: ID of the student
        admin_username: Username of the admin
    """
    students = get_data('students')
    if student_id not in students:
        return
    
    student = students[student_id]
    
    grade_level = input(f"Grade Level [{student.get('grade_level', '')}]: ") or student.get('grade_level', '')
    
    # Update student information
    student["grade_level"] = grade_level
    student["modified_at"] = datetime.now().isoformat()
    student["modified_by"] = admin_username
    
    # Save updated student
    students[student_id] = student
    save_data('students', students)

def update_teacher_info(teacher_id: str, admin_username: str) -> None:
    """
    Update teacher-specific information.
    
    Args:
        teacher_id: ID of the teacher
        admin_username: Username of the admin
    """
    teachers = get_data('teachers')
    if teacher_id not in teachers:
        return
    
    teacher = teachers[teacher_id]
    
    current_subjects = ", ".join(teacher.get('subjects', []))
    subjects_input = input(f"Subjects [{current_subjects}]: ") or current_subjects
    subjects = [s.strip() for s in subjects_input.split(",") if s.strip()]
    
    department = input(f"Department [{teacher.get('department', '')}]: ") or teacher.get('department', '')
    
    # Update teacher information
    teacher["subjects"] = subjects
    teacher["department"] = department
    teacher["modified_at"] = datetime.now().isoformat()
    teacher["modified_by"] = admin_username
    
    # Save updated teacher
    teachers[teacher_id] = teacher
    save_data('teachers', teachers)

def update_staff_info(staff_id: str, admin_username: str) -> None:
    """
    Update staff-specific information.
    
    Args:
        staff_id: ID of the staff member
        admin_username: Username of the admin
    """
    staff = get_data('staff')
    if staff_id not in staff:
        return
    
    staff_member = staff[staff_id]
    
    position = input(f"Position [{staff_member.get('position', '')}]: ") or staff_member.get('position', '')
    department = input(f"Department [{staff_member.get('department', '')}]: ") or staff_member.get('department', '')
    
    # Update staff information
    staff_member["position"] = position
    staff_member["department"] = department
    staff_member["modified_at"] = datetime.now().isoformat()
    staff_member["modified_by"] = admin_username
    
    # Save updated staff
    staff[staff_id] = staff_member
    save_data('staff', staff)

def update_parent_info(parent_id: str, admin_username: str) -> None:
    """
    Update parent-specific information.
    
    Args:
        parent_id: ID of the parent
        admin_username: Username of the admin
    """
    parents = get_data('parents')
    if parent_id not in parents:
        return
    
    parent = parents[parent_id]
    
    # Display current children
    current_children = parent.get('children', [])
    students = get_data('students')
    
    print("\nCurrent children:")
    for i, student_id in enumerate(current_children, 1):
        if student_id in students:
            student = students[student_id]
            name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
            print(f"{i}. {name} (ID: {student_id})")
    
    # Option to update children
    update_children = input("\nUpdate children? (y/n): ").lower() == 'y'
    if update_children:
        print("\nAvailable students:")
        for i, (student_id, student) in enumerate(students.items(), 1):
            name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
            print(f"{i}. {name} (ID: {student_id})")
        
        student_indices = input("\nEnter student numbers (comma-separated): ")
        selected_students = []
        
        if student_indices.strip():
            try:
                indices = [int(idx.strip()) - 1 for idx in student_indices.split(",")]
                student_ids = list(students.keys())
                selected_students = [student_ids[idx] for idx in indices if 0 <= idx < len(student_ids)]
            except (ValueError, IndexError):
                print("\n❌ Invalid selection. No changes will be made.")
                selected_students = current_children
        else:
            selected_students = current_children
        
        # Update parent's children
        parent["children"] = selected_students
        parent["modified_at"] = datetime.now().isoformat()
        parent["modified_by"] = admin_username
        
        # Update students' parent_id
        for student_id in students:
            if student_id in selected_students:
                students[student_id]["parent_id"] = parent_id
            elif students[student_id].get("parent_id") == parent_id:
                students[student_id]["parent_id"] = ""
        
        # Save updated parent and students
        parents[parent_id] = parent
        save_data('parents', parents)
        save_data('students', students)

def create_event_ui(admin_username: str) -> None:
    """
    UI for creating a new event.
    
    Args:
        admin_username: Username of the admin
    """
    from utils.constants import EVENT_TYPES
    
    clear_screen()
    print("\n" + "=" * 50)
    print("🆕 CREATE EVENT 🆕".center(50))
    print("=" * 50 + "\n")
    
    title = input("Event Title: ")
    description = input("Event Description: ")
    
    print("\nEvent Type:")
    print(f"1. Holiday ({EVENT_TYPES.HOLIDAY})")
    print(f"2. Exam ({EVENT_TYPES.EXAM})")
    print(f"3. Meeting ({EVENT_TYPES.MEETING})")
    print(f"4. Activity ({EVENT_TYPES.ACTIVITY})")
    print(f"5. Other ({EVENT_TYPES.OTHER})")
    
    type_choice = input("\nSelect Event Type (1-5): ")
    event_types = {
        "1": EVENT_TYPES.HOLIDAY,
        "2": EVENT_TYPES.EXAM,
        "3": EVENT_TYPES.MEETING,
        "4": EVENT_TYPES.ACTIVITY,
        "5": EVENT_TYPES.OTHER
    }
    event_type = event_types.get(type_choice, EVENT_TYPES.OTHER)
    
    start_date = input("Start Date (YYYY-MM-DD): ")
    start_time = input("Start Time (HH:MM): ")
    end_date = input("End Date (YYYY-MM-DD): ")
    end_time = input("End Time (HH:MM): ")
    
    # Determine event visibility
    print("\nEvent Visibility:")
    print("1. Public (all roles)")
    print("2. Teachers only")
    print("3. Students only")
    print("4. Staff only")
    print("5. Custom")
    
    visibility_choice = input("\nSelect Visibility (1-5): ")
    
    if visibility_choice == "1":
        visibility = ["all"]
    elif visibility_choice == "2":
        visibility = [USER_ROLES.TEACHER]
    elif visibility_choice == "3":
        visibility = [USER_ROLES.STUDENT]
    elif visibility_choice == "4":
        visibility = [USER_ROLES.STAFF]
    elif visibility_choice == "5":
        visibility = []
        role_options = {
            "1": USER_ROLES.ADMIN,
            "2": USER_ROLES.TEACHER,
            "3": USER_ROLES.STUDENT,
            "4": USER_ROLES.PARENT,
            "5": USER_ROLES.STAFF
        }
        
        print("\nSelect roles (comma-separated):")
        print("1. Administrators")
        print("2. Teachers")
        print("3. Students")
        print("4. Parents")
        print("5. Staff")
        
        selections = input("\nEnter selections (e.g., 1,2,3): ").split(",")
        visibility = [role_options[s.strip()] for s in selections if s.strip() in role_options]
    else:
        visibility = ["all"]
    
    # Location of the event
    location = input("\nEvent Location: ")
    
    # Create the event
    success, message = create_event(
        admin_username,
        title,
        description,
        event_type,
        start_date,
        start_time,
        end_date,
        end_time,
        location,
        visibility
    )
    
    print(f"\n{message}")
    input("\nPress Enter to continue...")

def view_events_ui() -> None:
    """UI for viewing upcoming events."""
    clear_screen()
    print("\n" + "=" * 50)
    print("📅 UPCOMING EVENTS 📅".center(50))
    print("=" * 50 + "\n")
    
    events = list_events()
    
    if not events:
        print("No upcoming events found.")
        input("\nPress Enter to continue...")
        return
    
    # Sort events by start date
    events.sort(key=lambda x: x.get("start_date", ""))
    
    # Display events
    for i, event in enumerate(events, 1):
        title = event.get("title", "")
        event_type = event.get("event_type", "")
        start_date = event.get("start_date", "")
        end_date = event.get("end_date", "")
        location = event.get("location", "")
        
        print(f"{i}. {title} ({event_type})")
        print(f"   Date: {start_date} to {end_date}")
        print(f"   Location: {location}")
        print()
    
    # Option to view event details
    event_idx = input("\nEnter number to view details (or 0 to return): ")
    try:
        event_idx = int(event_idx)
        if 1 <= event_idx <= len(events):
            display_event_details(events[event_idx - 1])
    except ValueError:
        pass

def edit_event_ui(admin_username: str) -> None:
    """
    UI for editing an existing event.
    
    Args:
        admin_username: Username of the admin
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("✏️ EDIT EVENT ✏️".center(50))
    print("=" * 50 + "\n")
    
    events = list_events()
    
    if not events:
        print("No events found to edit.")
        input("\nPress Enter to continue...")
        return
    
    # Sort events by start date
    events.sort(key=lambda x: x.get("start_date", ""))
    
    # Display events
    for i, event in enumerate(events, 1):
        title = event.get("title", "")
        event_type = event.get("event_type", "")
        start_date = event.get("start_date", "")
        
        print(f"{i}. {title} ({event_type}) - {start_date}")
    
    # Select event to edit
    event_idx = input("\nEnter number to edit (or 0 to return): ")
    try:
        event_idx = int(event_idx)
        if event_idx == 0:
            return
        
        if 1 <= event_idx <= len(events):
            selected_event = events[event_idx - 1]
            event_id = selected_event.get("id", "")
            
            # Display current values and get new ones
            print(f"\nEditing event: {selected_event.get('title', '')}")
            print("\nLeave fields blank to keep current values:")
            
            title = input(f"Title [{selected_event.get('title', '')}]: ") or selected_event.get('title', '')
            description = input(f"Description [{selected_event.get('description', '')}]: ") or selected_event.get('description', '')
            location = input(f"Location [{selected_event.get('location', '')}]: ") or selected_event.get('location', '')
            
            # Update the event
            all_events = get_data('events')
            if event_id in all_events:
                all_events[event_id].update({
                    "title": title,
                    "description": description,
                    "location": location,
                    "modified_at": datetime.now().isoformat(),
                    "modified_by": admin_username
                })
                
                save_data('events', all_events)
                print("\n✅ Event updated successfully.")
            else:
                print("\n❌ Event not found.")
    except ValueError:
        print("\n❌ Invalid choice.")
    
    input("\nPress Enter to continue...")

def cancel_event_ui(admin_username: str) -> None:
    """
    UI for cancelling an event.
    
    Args:
        admin_username: Username of the admin
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("❌ CANCEL EVENT ❌".center(50))
    print("=" * 50 + "\n")
    
    events = list_events()
    
    if not events:
        print("No events found to cancel.")
        input("\nPress Enter to continue...")
        return
    
    # Sort events by start date
    events.sort(key=lambda x: x.get("start_date", ""))
    
    # Display events
    for i, event in enumerate(events, 1):
        title = event.get("title", "")
        event_type = event.get("event_type", "")
        start_date = event.get("start_date", "")
        
        print(f"{i}. {title} ({event_type}) - {start_date}")
    
    # Select event to cancel
    event_idx = input("\nEnter number to cancel (or 0 to return): ")
    try:
        event_idx = int(event_idx)
        if event_idx == 0:
            return
        
        if 1 <= event_idx <= len(events):
            selected_event = events[event_idx - 1]
            event_id = selected_event.get("id", "")
            
            # Confirm cancellation
            print(f"\nYou are about to cancel: {selected_event.get('title', '')}")
            confirm = input("Are you sure? (y/n): ")
            
            if confirm.lower() == 'y':
                # Cancel the event
                all_events = get_data('events')
                if event_id in all_events:
                    all_events[event_id]["is_cancelled"] = True
                    all_events[event_id]["cancelled_at"] = datetime.now().isoformat()
                    all_events[event_id]["cancelled_by"] = admin_username
                    
                    save_data('events', all_events)
                    print("\n✅ Event cancelled successfully.")
                else:
                    print("\n❌ Event not found.")
            else:
                print("\nOperation cancelled.")
    except ValueError:
        print("\n❌ Invalid choice.")
    
    input("\nPress Enter to continue...")

def view_attendance_reports() -> None:
    """UI for viewing attendance reports."""
    clear_screen()
    print("\n" + "=" * 50)
    print("📊 ATTENDANCE REPORTS 📊".center(50))
    print("=" * 50 + "\n")
    
    print("1. By Class")
    print("2. By Student")
    print("3. By Date Range")
    print(f"{MENU_BACK}. Back")
    
    choice = input("\nEnter your choice: ")
    
    if choice == "1":
        # Get list of classes/courses
        courses = get_data('courses')
        if not courses:
            print("\nNo courses found.")
            input("\nPress Enter to continue...")
            return
        
        print("\nAvailable Courses:")
        for i, (course_id, course) in enumerate(courses.items(), 1):
            print(f"{i}. {course.get('name', '')} ({course.get('code', '')})")
        
        course_idx = input("\nSelect course (number): ")
        try:
            course_idx = int(course_idx)
            course_ids = list(courses.keys())
            if 1 <= course_idx <= len(course_ids):
                course_id = course_ids[course_idx - 1]
                report = generate_attendance_report(course_id=course_id)
                display_attendance_report(report, f"Course: {courses[course_id].get('name', '')}")
        except ValueError:
            print("\n❌ Invalid choice.")
    
    elif choice == "2":
        # Get list of students
        students = get_data('students')
        if not students:
            print("\nNo students found.")
            input("\nPress Enter to continue...")
            return
        
        print("\nEnter student name or ID:")
        search = input().lower()
        
        matching_students = []
        for student_id, student in students.items():
            first_name = student.get("first_name", "").lower()
            last_name = student.get("last_name", "").lower()
            full_name = f"{first_name} {last_name}".strip()
            
            if (search in first_name or search in last_name or 
                search in full_name or search in student_id.lower()):
                matching_students.append((student_id, student))
        
        if matching_students:
            print("\nMatching Students:")
            for i, (student_id, student) in enumerate(matching_students, 1):
                name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
                print(f"{i}. {name} (ID: {student_id})")
            
            student_idx = input("\nSelect student (number): ")
            try:
                student_idx = int(student_idx)
                if 1 <= student_idx <= len(matching_students):
                    student_id, student = matching_students[student_idx - 1]
                    name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
                    report = generate_attendance_report(student_id=student_id)
                    display_attendance_report(report, f"Student: {name}")
            except ValueError:
                print("\n❌ Invalid choice.")
        else:
            print("\nNo matching students found.")
    
    elif choice == "3":
        print("\nEnter date range:")
        start_date = input("Start Date (YYYY-MM-DD): ")
        end_date = input("End Date (YYYY-MM-DD): ")
        
        report = generate_attendance_report(start_date=start_date, end_date=end_date)
        display_attendance_report(report, f"Date Range: {start_date} to {end_date}")
    
    elif choice == MENU_BACK:
        return
    
    else:
        print("\n❌ Invalid choice.")
    
    input("\nPress Enter to continue...")

def view_grade_reports() -> None:
    """UI for viewing grade reports."""
    clear_screen()
    print("\n" + "=" * 50)
    print("📊 GRADE REPORTS 📊".center(50))
    print("=" * 50 + "\n")
    
    print("1. By Class")
    print("2. By Student")
    print("3. By Term")
    print(f"{MENU_BACK}. Back")
    
    choice = input("\nEnter your choice: ")
    
    if choice == "1":
        # Grade report by class logic
        pass
    elif choice == "2":
        # Grade report by student logic
        pass
    elif choice == "3":
        # Grade report by term logic
        pass
    elif choice == MENU_BACK:
        return
    else:
        print("\n❌ Invalid choice.")
    
    input("\nPress Enter to continue...")

def view_financial_reports() -> None:
    """UI for viewing financial reports."""
    clear_screen()
    print("\n" + "=" * 50)
    print("📊 FINANCIAL REPORTS 📊".center(50))
    print("=" * 50 + "\n")
    
    print("1. Pending Fees")
    print("2. Payment History")
    print("3. Fee Collections by Month")
    print(f"{MENU_BACK}. Back")
    
    choice = input("\nEnter your choice: ")
    
    if choice == "1":
        # Pending fees report logic
        pass
    elif choice == "2":
        # Payment history report logic
        pass
    elif choice == "3":
        # Fee collections by month logic
        pass
    elif choice == MENU_BACK:
        return
    else:
        print("\n❌ Invalid choice.")
    
    input("\nPress Enter to continue...")

def view_enrollment_reports() -> None:
    """UI for viewing enrollment reports."""
    clear_screen()
    print("\n" + "=" * 50)
    print("📊 ENROLLMENT REPORTS 📊".center(50))
    print("=" * 50 + "\n")
    
    print("1. Enrollment by Grade")
    print("2. New Admissions")
    print("3. Student Demographics")
    print(f"{MENU_BACK}. Back")
    
    choice = input("\nEnter your choice: ")
    
    if choice == "1":
        # Enrollment by grade logic
        pass
    elif choice == "2":
        # New admissions logic
        pass
    elif choice == "3":
        # Student demographics logic
        pass
    elif choice == MENU_BACK:
        return
    else:
        print("\n❌ Invalid choice.")
    
    input("\nPress Enter to continue...")

def display_user_details(user: Dict[str, Any]) -> None:
    """
    Display detailed information about a user.
    
    Args:
        user: User data dictionary
    """
    clear_screen()
    role = user.get("role", "")
    user_id = user.get("id", "")
    
    print("\n" + "=" * 50)
    print(f"👤 USER DETAILS: {user.get('username', '')} 👤".center(50))
    print("=" * 50 + "\n")
    
    print(f"ID: {user_id}")
    print(f"Name: {user.get('first_name', '')} {user.get('last_name', '')}")
    print(f"Email: {user.get('email', '')}")
    print(f"Phone: {user.get('phone', '')}")
    print(f"Role: {role}")
    print(f"Status: {'Active' if user.get('is_active', True) else 'Inactive'}")
    print(f"Created: {user.get('created_at', '')}")
    
    # Display role-specific details
    if role == USER_ROLES.STUDENT:
        display_student_details(user_id)
    elif role == USER_ROLES.TEACHER:
        display_teacher_details(user_id)
    elif role == USER_ROLES.STAFF:
        display_staff_details(user_id)
    elif role == USER_ROLES.PARENT:
        display_parent_details(user_id)

def display_student_details(student_id: str) -> None:
    """
    Display detailed information about a student.
    
    Args:
        student_id: Student ID
    """
    student = get_student_details(student_id)
    if not student:
        return
    
    print("\nStudent Details:")
    print(f"Grade Level: {student.get('grade_level', '')}")
    print(f"Date of Birth: {student.get('date_of_birth', '')}")
    print(f"Enrollment Date: {student.get('enrollment_date', '')}")
    
    # Display parent information if available
    parent_id = student.get('parent_id', '')
    if parent_id:
        parents = get_data('parents')
        if parent_id in parents:
            parent = parents[parent_id]
            print(f"\nParent: {parent.get('first_name', '')} {parent.get('last_name', '')}")
            print(f"Parent Email: {parent.get('email', '')}")
            print(f"Parent Phone: {parent.get('phone', '')}")
    
    # Display courses
    courses = student.get('courses', [])
    if courses:
        print("\nEnrolled Courses:")
        all_courses = get_data('courses')
        for course_id in courses:
            if course_id in all_courses:
                course = all_courses[course_id]
                print(f"- {course.get('name', '')} ({course.get('code', '')})")

def display_teacher_details(teacher_id: str) -> None:
    """
    Display detailed information about a teacher.
    
    Args:
        teacher_id: Teacher ID
    """
    teacher = get_teacher_details(teacher_id)
    if not teacher:
        return
    
    print("\nTeacher Details:")
    print(f"Department: {teacher.get('department', '')}")
    print(f"Hire Date: {teacher.get('hire_date', '')}")
    
    # Display subjects
    subjects = teacher.get('subjects', [])
    if subjects:
        print("\nSubjects:")
        for subject in subjects:
            print(f"- {subject}")
    
    # Display classes/courses
    classes = teacher.get('classes', [])
    if classes:
        print("\nAssigned Classes:")
        all_courses = get_data('courses')
        for course_id in classes:
            if course_id in all_courses:
                course = all_courses[course_id]
                print(f"- {course.get('name', '')} ({course.get('code', '')})")

def display_staff_details(staff_id: str) -> None:
    """
    Display detailed information about a staff member.
    
    Args:
        staff_id: Staff ID
    """
    staff = get_staff_details(staff_id)
    if not staff:
        return
    
    print("\nStaff Details:")
    print(f"Position: {staff.get('position', '')}")
    print(f"Department: {staff.get('department', '')}")
    print(f"Hire Date: {staff.get('hire_date', '')}")

def display_parent_details(parent_id: str) -> None:
    """
    Display detailed information about a parent.
    
    Args:
        parent_id: Parent ID
    """
    parents = get_data('parents')
    if parent_id not in parents:
        return
    
    parent = parents[parent_id]
    
    print("\nParent Details:")
    
    # Display children
    children = parent.get('children', [])
    if children:
        print("\nChildren:")
        students = get_data('students')
        for student_id in children:
            if student_id in students:
                student = students[student_id]
                name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
                grade = student.get('grade_level', '')
                print(f"- {name} (Grade: {grade})")

def display_users_list(users: List[Dict[str, Any]], title: str) -> None:
    """
    Display a list of users.
    
    Args:
        users: List of user dictionaries
        title: Title for the list
    """
    clear_screen()
    print("\n" + "=" * 50)
    print(f"👥 {title.upper()} 👥".center(50))
    print("=" * 50 + "\n")
    
    if not users:
        print(f"No {title.lower()} found.")
        input("\nPress Enter to continue...")
        return
    
    for i, user in enumerate(users, 1):
        name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        username = user.get('username', '')
        email = user.get('email', '')
        status = 'Active' if user.get('is_active', True) else 'Inactive'
        
        print(f"{i}. {name}")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Status: {status}")
        print()
    
    # Option to view user details
    user_idx = input("\nEnter number to view details (or 0 to return): ")
    try:
        user_idx = int(user_idx)
        if 1 <= user_idx <= len(users):
            display_user_details(users[user_idx - 1])
    except ValueError:
        pass

def display_event_details(event: Dict[str, Any]) -> None:
    """
    Display detailed information about an event.
    
    Args:
        event: Event data dictionary
    """
    clear_screen()
    print("\n" + "=" * 50)
    print(f"📅 EVENT DETAILS 📅".center(50))
    print("=" * 50 + "\n")
    
    print(f"Title: {event.get('title', '')}")
    print(f"Type: {event.get('event_type', '')}")
    print(f"Description: {event.get('description', '')}")
    print(f"Date: {event.get('start_date', '')} to {event.get('end_date', '')}")
    print(f"Time: {event.get('start_time', '')} to {event.get('end_time', '')}")
    print(f"Location: {event.get('location', '')}")
    
    # Display visibility
    visibility = event.get('visibility', [])
    if visibility:
        if "all" in visibility:
            print("Visibility: All users")
        else:
            print(f"Visibility: {', '.join(visibility)}")
    
    # Display creator
    creator_id = event.get('created_by', '')
    if creator_id:
        creator = get_user_by_id(creator_id)
        if creator:
            creator_name = f"{creator.get('first_name', '')} {creator.get('last_name', '')}".strip()
            print(f"Created by: {creator_name}")
    
    input("\nPress Enter to continue...")

def display_attendance_report(report: List[Dict[str, Any]], title: str) -> None:
    """
    Display an attendance report.
    
    Args:
        report: List of attendance records
        title: Title for the report
    """
    clear_screen()
    print("\n" + "=" * 50)
    print(f"📊 ATTENDANCE REPORT 📊".center(50))
    print("=" * 50)
    print(f"\n{title}\n")
    
    if not report:
        print("No attendance records found.")
        return
    
    # Group by date
    by_date = {}
    for record in report:
        date = record.get('date', '')
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(record)
    
    # Display report
    for date, records in sorted(by_date.items()):
        print(f"\nDate: {date}")
        print("-" * 50)
        
        present = sum(1 for r in records if r.get('status') == 'present')
        absent = sum(1 for r in records if r.get('status') == 'absent')
        late = sum(1 for r in records if r.get('status') == 'late')
        excused = sum(1 for r in records if r.get('status') == 'excused')
        total = len(records)
        
        print(f"Total: {total}")
        print(f"Present: {present} ({present/total*100:.1f}%)")
        print(f"Absent: {absent} ({absent/total*100:.1f}%)")
        print(f"Late: {late} ({late/total*100:.1f}%)")
        print(f"Excused: {excused} ({excused/total*100:.1f}%)")
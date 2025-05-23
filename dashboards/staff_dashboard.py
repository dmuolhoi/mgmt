"""
Staff Dashboard Module
Handles functionality for non-teaching staff interface
"""
from datetime import datetime
from typing import Dict, Any
from utils.helpers import clear_screen
from utils.constants import MENU_BACK, MENU_LOGOUT
from services.staff_service import (
    log_facility_issue,
    request_leave,
    get_staff_details
)

def staff_dashboard(staff_id: str) -> None:
    """
    Display and handle the staff dashboard functionality.
    
    Args:
        staff_id: The ID of the staff member
    """
    staff = get_staff_details(staff_id)
    if not staff:
        print("❌ Access denied: Staff privileges required")
        return
    
    username = staff["username"]
    
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print(f"👨‍💼 STAFF DASHBOARD: {username} 👩‍💼".center(50))
        print("=" * 50)
        
        print("\n1. View Daily Duties")
        print("2. Log Facility Issue")
        print("3. View Notice Board")
        print("4. Request Leave")
        print("5. Student Management")
        print("6. Fee Management")
        print(f"\n{MENU_LOGOUT}. Logout")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            view_daily_duties(staff_id)
        elif choice == "2":
            log_facility_issue_ui(staff_id)
        elif choice == "3":
            view_notice_board()
        elif choice == "4":
            request_leave_ui(staff_id)
        elif choice == "5":
            student_management_menu(staff_id)
        elif choice == "6":
            fee_management_menu(staff_id)
        elif choice == MENU_LOGOUT:
            print("\nLogging out...")
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

def view_daily_duties(staff_id: str) -> None:
    """
    Display daily duties for the staff member.
    
    Args:
        staff_id: ID of the staff member
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📋 DAILY DUTIES 📋".center(50))
    print("=" * 50 + "\n")
    
    staff = get_staff_details(staff_id)
    if not staff:
        print("❌ Staff details not found.")
        input("\nPress Enter to continue...")
        return
    
    duties = staff.get("duties", [])
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Filter duties for today
    today_duties = [
        duty for duty in duties 
        if duty.get("date") == today and duty.get("status") != "completed"
    ]
    
    if not today_duties:
        print("No duties assigned for today.")
    else:
        for i, duty in enumerate(today_duties, 1):
            print(f"{i}. {duty.get('description', '')}")
            print(f"   Time: {duty.get('time', '')}")
            print(f"   Status: {duty.get('status', '').title()}")
            print()
    
    input("\nPress Enter to continue...")

def log_facility_issue_ui(staff_id: str) -> None:
    """
    UI for logging facility issues.
    
    Args:
        staff_id: ID of the staff member
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("🔧 LOG FACILITY ISSUE 🔧".center(50))
    print("=" * 50 + "\n")
    
    # Get issue details
    location = input("Location: ")
    description = input("Description: ")
    priority = input("Priority (low/medium/high): ").lower()
    
    if priority not in ["low", "medium", "high"]:
        priority = "medium"
    
    issue = {
        "location": location,
        "description": description,
        "priority": priority
    }
    
    success, message = log_facility_issue(staff_id, issue)
    print(f"\n{message}")
    input("\nPress Enter to continue...")

def view_notice_board() -> None:
    """Display the notice board with announcements."""
    from services.event_service import get_upcoming_events
    
    clear_screen()
    print("\n" + "=" * 50)
    print("📢 NOTICE BOARD 📢".center(50))
    print("=" * 50 + "\n")
    
    # Get upcoming events
    events = get_upcoming_events(role="staff", limit=5)
    
    print("Upcoming Events:")
    if events:
        for event in events:
            print(f"\n- {event.get('title', '')}")
            print(f"  Date: {event.get('start_date', '')}")
            print(f"  Location: {event.get('location', '')}")
    else:
        print("\nNo upcoming events.")
    
    input("\nPress Enter to continue...")

def request_leave_ui(staff_id: str) -> None:
    """
    UI for submitting leave requests.
    
    Args:
        staff_id: ID of the staff member
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📅 REQUEST LEAVE 📅".center(50))
    print("=" * 50 + "\n")
    
    # Get leave request details
    start_date = input("Start Date (YYYY-MM-DD): ")
    end_date = input("End Date (YYYY-MM-DD): ")
    reason = input("Reason for Leave: ")
    
    leave_request = {
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason,
        "type": "regular"  # Can be extended to support different leave types
    }
    
    success, message = request_leave(staff_id, leave_request)
    print(f"\n{message}")
    input("\nPress Enter to continue...")

def student_management_menu(staff_id: str) -> None:
    """
    Display and handle the student management menu.
    
    Args:
        staff_id: ID of the staff member
    """
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print("👨‍🎓 STUDENT MANAGEMENT 👩‍🎓".center(50))
        print("=" * 50 + "\n")
        
        print("1. Add New Student")
        print("2. Edit Student Details")
        print("3. View Student List")
        print(f"\n{MENU_BACK}. Back")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            add_student_ui(staff_id)
        elif choice == "2":
            edit_student_ui(staff_id)
        elif choice == "3":
            view_student_list()
        elif choice == MENU_BACK:
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

def fee_management_menu(staff_id: str) -> None:
    """
    Display and handle the fee management menu.
    
    Args:
        staff_id: ID of the staff member
    """
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print("💰 FEE MANAGEMENT 💰".center(50))
        print("=" * 50 + "\n")
        
        print("1. View Pending Fees")
        print("2. Mark Fees as Paid")
        print("3. Send Fee Report to Admin")
        print(f"\n{MENU_BACK}. Back")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            view_pending_fees()
        elif choice == "2":
            mark_fees_paid_ui()
        elif choice == "3":
            send_fees_report_to_admin(staff_id)
        elif choice == MENU_BACK:
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

def add_student_ui(staff_id: str) -> None:
    """
    UI for adding a new student.
    
    Args:
        staff_id: ID of the staff member
    """
    from services.student_service import add_student
    
    clear_screen()
    print("\n" + "=" * 50)
    print("➕ ADD NEW STUDENT ➕".center(50))
    print("=" * 50 + "\n")
    
    # Get student details
    username = input("Username: ")
    password = input("Password: ")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    email = input("Email: ")
    phone = input("Phone: ")
    grade_level = input("Grade Level: ")
    date_of_birth = input("Date of Birth (YYYY-MM-DD): ")
    
    success, message = add_student(
        staff_id, username, password, first_name, last_name,
        email, phone, grade_level, date_of_birth
    )
    
    print(f"\n{message}")
    input("\nPress Enter to continue...")

def edit_student_ui(staff_id: str) -> None:
    """
    UI for editing student details.
    
    Args:
        staff_id: ID of the staff member
    """
    from services.student_service import get_student_details, update_student
    
    clear_screen()
    print("\n" + "=" * 50)
    print("✏️ EDIT STUDENT DETAILS ✏️".center(50))
    print("=" * 50 + "\n")
    
    student_id = input("Enter Student ID: ")
    
    student = get_student_details(student_id)
    if not student:
        print("\n❌ Student not found.")
        input("\nPress Enter to continue...")
        return
    
    print("\nCurrent Details:")
    print(f"Name: {student.get('first_name', '')} {student.get('last_name', '')}")
    print(f"Email: {student.get('email', '')}")
    print(f"Phone: {student.get('phone', '')}")
    print(f"Grade Level: {student.get('grade_level', '')}")
    
    print("\nEnter new details (leave blank to keep current):")
    
    update_data = {}
    
    first_name = input("First Name: ")
    if first_name:
        update_data["first_name"] = first_name
    
    last_name = input("Last Name: ")
    if last_name:
        update_data["last_name"] = last_name
    
    email = input("Email: ")
    if email:
        update_data["email"] = email
    
    phone = input("Phone: ")
    if phone:
        update_data["phone"] = phone
    
    grade_level = input("Grade Level: ")
    if grade_level:
        update_data["grade_level"] = grade_level
    
    if update_data:
        success, message = update_student(student_id, update_data, staff_id)
        print(f"\n{message}")
    else:
        print("\nNo changes made.")
    
    input("\nPress Enter to continue...")

def view_student_list() -> None:
    """Display list of students."""
    from services.student_service import get_students_by_grade
    
    clear_screen()
    print("\n" + "=" * 50)
    print("📋 STUDENT LIST 📋".center(50))
    print("=" * 50 + "\n")
    
    grade_level = input("Enter Grade Level (or press Enter for all): ")
    
    if grade_level:
        students = get_students_by_grade(grade_level)
        print(f"\nStudents in Grade {grade_level}:")
    else:
        from storage.datastore import get_data
        students = get_data('students')
        print("\nAll Students:")
    
    if not students:
        print("\nNo students found.")
    else:
        for student in students:
            print(f"\nID: {student.get('id', '')}")
            print(f"Name: {student.get('first_name', '')} {student.get('last_name', '')}")
            print(f"Grade: {student.get('grade_level', '')}")
    
    input("\nPress Enter to continue...")

def view_pending_fees() -> None:
    """Display list of students with pending fees."""
    clear_screen()
    print("\n" + "=" * 50)
    print("💰 PENDING FEES 💰".center(50))
    print("=" * 50 + "\n")
    
    from storage.datastore import get_data
    fees = get_data('fees')
    
    pending_fees = [
        fee for fee in fees.values()
        if fee.get("status") == "pending"
    ]
    
    if not pending_fees:
        print("No pending fees found.")
    else:
        for fee in pending_fees:
            student_id = fee.get("student_id", "")
            amount = fee.get("amount", 0)
            due_date = fee.get("due_date", "")
            
            # Get student name
            students = get_data('students')
            student = students.get(student_id, {})
            student_name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
            
            print(f"\nStudent: {student_name}")
            print(f"Amount: ${amount:.2f}")
            print(f"Due Date: {due_date}")
    
    input("\nPress Enter to continue...")

def mark_fees_paid_ui() -> None:
    """UI for marking fees as paid."""
    clear_screen()
    print("\n" + "=" * 50)
    print("✅ MARK FEES PAID ✅".center(50))
    print("=" * 50 + "\n")
    
    from storage.datastore import get_data, save_data
    
    student_id = input("Enter Student ID: ")
    amount = float(input("Enter Amount Paid: $"))
    payment_date = datetime.now().isoformat()
    
    fees = get_data('fees')
    
    # Find pending fees for this student
    student_fees = [
        (fee_id, fee) for fee_id, fee in fees.items()
        if fee.get("student_id") == student_id and fee.get("status") == "pending"
    ]
    
    if not student_fees:
        print("\n❌ No pending fees found for this student.")
    else:
        for fee_id, fee in student_fees:
            if amount >= fee["amount"]:
                fee["status"] = "paid"
                fee["paid_date"] = payment_date
                fee["payment_amount"] = fee["amount"]
                amount -= fee["amount"]
                print(f"\n✅ Marked fee of ${fee['amount']:.2f} as paid.")
            elif amount > 0:
                # Partial payment
                fee["status"] = "partial"
                fee["paid_date"] = payment_date
                fee["payment_amount"] = amount
                print(f"\n✅ Recorded partial payment of ${amount:.2f}.")
                amount = 0
            
            if amount <= 0:
                break
        
        save_data('fees', fees)
        
        if amount > 0:
            print(f"\nℹ️ Excess payment: ${amount:.2f}")
    
    input("\nPress Enter to continue...")

def send_fees_report_to_admin(staff_id: str) -> None:
    """
    Send a fee report to the admin.
    
    Args:
        staff_id: ID of the staff member
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📊 SEND FEE REPORT 📊".center(50))
    print("=" * 50 + "\n")
    
    from storage.datastore import get_data
    fees = get_data('fees')
    
    # Calculate statistics
    total_fees = sum(fee.get("amount", 0) for fee in fees.values())
    paid_fees = sum(
        fee.get("amount", 0) 
        for fee in fees.values() 
        if fee.get("status") == "paid"
    )
    pending_fees = sum(
        fee.get("amount", 0) 
        for fee in fees.values() 
        if fee.get("status") == "pending"
    )
    
    # Create report
    report = {
        "generated_by": staff_id,
        "generated_at": datetime.now().isoformat(),
        "total_fees": total_fees,
        "paid_fees": paid_fees,
        "pending_fees": pending_fees,
        "status": "pending_review"
    }
    
    # Save report
    reports = get_data('reports')
    report_id = f"REP{len(reports) + 1:04d}"
    reports[report_id] = report
    
    from storage.datastore import save_data
    save_data('reports', reports)
    
    print(f"\n✅ Fee report sent to admin. Report ID: {report_id}")
    input("\nPress Enter to continue...")
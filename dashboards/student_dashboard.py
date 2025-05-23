"""
Student dashboard for the School Management System
"""
from datetime import datetime
from typing import Dict, Any, List
from utils.helpers import clear_screen, get_user_by_id
from utils.constants import USER_ROLES, MENU_BACK, MENU_LOGOUT
from storage.datastore import get_data, save_data
from services.event_service import get_upcoming_events
from services.student_service import get_student_courses, get_student_grades

def student_dashboard(student_id: str) -> None:
    """
    Display the student dashboard.
    
    Args:
        student_id: The ID of the student user
    """
    student = get_user_by_id(student_id)
    if not student or student["role"] != USER_ROLES.STUDENT:
        print("❌ Access denied: Student privileges required")
        return
    
    username = student["username"]
    
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print(f"👨‍🎓 STUDENT DASHBOARD: {username} 👩‍🎓".center(50))
        print("=" * 50)
        
        # Show upcoming events and due assignments
        print("\n📅 Upcoming Events:")
        upcoming_events = get_upcoming_events(USER_ROLES.STUDENT, 2)
        if upcoming_events:
            for event in upcoming_events:
                print(f"- {event['title']} ({event['start_date']})")
        else:
            print("- No upcoming events")
        
        print("\n📚 Due Assignments:")
        due_assignments = get_due_assignments(student_id, 2)
        if due_assignments:
            for assignment in due_assignments:
                print(f"- {assignment['title']} ({assignment['due_date']})")
        else:
            print("- No assignments due soon")
        
        print("\n" + "-" * 50)
        print("1. View Grades")
        print("2. View Attendance")
        print("3. Submit Assignment")
        print("4. View Course Materials")
        print("5. View School Announcements")
        print(f"\n{MENU_LOGOUT}. Logout")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            view_grades_ui(student_id)
        elif choice == "2":
            view_attendance_ui(student_id)
        elif choice == "3":
            submit_assignment_ui(student_id)
        elif choice == "4":
            view_course_materials_ui(student_id)
        elif choice == "5":
            view_announcements_ui(USER_ROLES.STUDENT)
        elif choice == MENU_LOGOUT:
            print("\nLogging out...")
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

def get_due_assignments(student_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get assignments due soon for a student.
    
    Args:
        student_id: ID of the student
        limit: Maximum number of assignments to return
    
    Returns:
        List of assignment dictionaries
    """
    # Get student's courses
    student_courses = get_student_courses(student_id)
    course_ids = [course.get("id", "") for course in student_courses]
    
    # Get assignments for these courses
    assignments = get_data('assignments')
    
    # Filter assignments that are active and due in the future
    today = datetime.now().strftime("%Y-%m-%d")
    
    due_assignments = []
    submissions = get_data('submissions')
    
    for assignment_id, assignment in assignments.items():
        if assignment.get("course_id") in course_ids and assignment.get("status") == "active":
            due_date = assignment.get("due_date", "")
            
            if due_date >= today:
                # Check if already submitted
                is_submitted = False
                for submission in submissions.values():
                    if (submission.get("assignment_id") == assignment_id and 
                        submission.get("student_id") == student_id):
                        is_submitted = True
                        break
                
                if not is_submitted:
                    due_assignments.append({
                        "id": assignment_id,
                        **assignment
                    })
    
    # Sort by due date
    due_assignments.sort(key=lambda x: x.get("due_date", ""))
    
    # Return limited number of assignments
    return due_assignments[:limit]

def view_grades_ui(student_id: str) -> None:
    """
    UI for viewing grades.
    
    Args:
        student_id: ID of the student
    """
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print("📊 MY GRADES 📊".center(50))
        print("=" * 50 + "\n")
        
        print("1. View All Grades")
        print("2. View Grades by Course")
        print("3. View Grade Summaries")
        print(f"\n{MENU_BACK}. Back")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            view_all_grades(student_id)
        elif choice == "2":
            view_grades_by_course(student_id)
        elif choice == "3":
            view_grade_summaries(student_id)
        elif choice == MENU_BACK:
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

def view_all_grades(student_id: str) -> None:
    """
    View all grades for a student.
    
    Args:
        student_id: ID of the student
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📝 ALL GRADES 📝".center(50))
    print("=" * 50 + "\n")
    
    # Get student's grades
    student_grades = get_student_grades(student_id)
    
    if not student_grades:
        print("You don't have any grades yet.")
        input("\nPress Enter to continue...")
        return
    
    # Sort by graded_at (newest first)
    student_grades.sort(key=lambda x: x.get("graded_at", ""), reverse=True)
    
    # Organize grades by course
    grades_by_course = {}
    
    for grade in student_grades:
        course_id = grade.get("course_id", "")
        
        if course_id not in grades_by_course:
            grades_by_course[course_id] = []
        
        grades_by_course[course_id].append(grade)
    
    # Display grades
    courses = get_data('courses')
    assignments = get_data('assignments')
    
    for course_id, course_grades in grades_by_course.items():
        course_name = "Unknown Course"
        if course_id in courses:
            course_name = courses[course_id].get("name", "Unknown Course")
        
        print(f"\n{course_name}:")
        print("-" * 50)
        
        for grade in course_grades:
            assignment_id = grade.get("assignment_id", "")
            assignment_name = "Unknown Assignment"
            
            if assignment_id in assignments:
                assignment_name = assignments[assignment_id].get("title", "Unknown Assignment")
            
            points = grade.get("points", 0)
            max_points = grade.get("max_points", 0)
            percentage = grade.get("percentage", 0)
            letter_grade = grade.get("letter_grade", "")
            graded_at = grade.get("graded_at", "")
            
            print(f"{assignment_name}")
            print(f"  Score: {points}/{max_points} ({percentage:.1f}%) - {letter_grade}")
            print(f"  Date: {graded_at}")
            
            comments = grade.get("comments", "")
            if comments:
                print(f"  Comments: {comments}")
            
            print()
    
    input("\nPress Enter to continue...")

def view_grades_by_course(student_id: str) -> None:
    """
    View grades by course for a student.
    
    Args:
        student_id: ID of the student
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📝 GRADES BY COURSE 📝".center(50))
    print("=" * 50 + "\n")
    
    # Get student's courses
    student_courses = get_student_courses(student_id)
    
    if not student_courses:
        print("You are not enrolled in any courses.")
        input("\nPress Enter to continue...")
        return
    
    # Display courses
    print("Select a course:")
    for i, course in enumerate(student_courses, 1):
        print(f"{i}. {course.get('name', '')} ({course.get('code', '')})")
    
    print(f"\n{MENU_BACK}. Back")
    
    choice = input("\nEnter your choice: ")
    
    if choice == MENU_BACK:
        return
    
    try:
        course_idx = int(choice) - 1
        if 0 <= course_idx < len(student_courses):
            selected_course = student_courses[course_idx]
            view_course_grades(student_id, selected_course)
        else:
            print("\n❌ Invalid choice.")
            input("\nPress Enter to continue...")
    except ValueError:
        print("\n❌ Invalid choice. Please enter a number.")
        input("\nPress Enter to continue...")

def view_course_grades(student_id: str, course: Dict[str, Any]) -> None:
    """
    View grades for a specific course.
    
    Args:
        student_id: ID of the student
        course: Course data dictionary
    """
    course_id = course.get("id", "")
    course_name = course.get("name", "")
    
    clear_screen()
    print("\n" + "=" * 50)
    print(f"📝 GRADES: {course_name} 📝".center(50))
    print("=" * 50 + "\n")
    
    # Get student's grades for this course
    grades = get_data('grades')
    
    course_grades = []
    for grade_id, grade in grades.items():
        if grade.get("student_id") == student_id and grade.get("course_id") == course_id:
            course_grades.append({
                "id": grade_id,
                **grade
            })
    
    if not course_grades:
        print("No grades available for this course.")
        input("\nPress Enter to continue...")
        return
    
    # Sort by graded_at
    course_grades.sort(key=lambda x: x.get("graded_at", ""))
    
    # Calculate course average
    total_percentage = sum(grade.get("percentage", 0) for grade in course_grades)
    average_percentage = total_percentage / len(course_grades)
    
    # Get letter grade for average
    from utils.helpers import calculate_grade_letter
    average_letter = calculate_grade_letter(average_percentage)
    
    print(f"Course Average: {average_percentage:.1f}% ({average_letter})\n")
    
    # Display grades
    assignments = get_data('assignments')
    
    for grade in course_grades:
        assignment_id = grade.get("assignment_id", "")
        assignment_name = "Unknown Assignment"
        assignment_type = "Unknown Type"
        
        if assignment_id in assignments:
            assignment_name = assignments[assignment_id].get("title", "Unknown Assignment")
            assignment_type = assignments[assignment_id].get("type", "Unknown Type")
        
        points = grade.get("points", 0)
        max_points = grade.get("max_points", 0)
        percentage = grade.get("percentage", 0)
        letter_grade = grade.get("letter_grade", "")
        graded_at = grade.get("graded_at", "")
        
        print(f"{assignment_name} ({assignment_type})")
        print(f"  Score: {points}/{max_points} ({percentage:.1f}%) - {letter_grade}")
        print(f"  Date: {graded_at}")
        
        comments = grade.get("comments", "")
        if comments:
            print(f"  Comments: {comments}")
        
        print()
    
    input("\nPress Enter to continue...")

def view_grade_summaries(student_id: str) -> None:
    """
    View grade summaries for a student.
    
    Args:
        student_id: ID of the student
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📊 GRADE SUMMARIES 📊".center(50))
    print("=" * 50 + "\n")
    
    # Get student's courses
    student_courses = get_student_courses(student_id)
    
    if not student_courses:
        print("You are not enrolled in any courses.")
        input("\nPress Enter to continue...")
        return
    
    # Get student's grades
    grades = get_data('grades')
    
    # Calculate course averages
    course_averages = []
    
    for course in student_courses:
        course_id = course.get("id", "")
        course_name = course.get("name", "")
        
        course_grades = []
        for grade_id, grade in grades.items():
            if grade.get("student_id") == student_id and grade.get("course_id") == course_id:
                course_grades.append(grade)
        
        if course_grades:
            total_percentage = sum(grade.get("percentage", 0) for grade in course_grades)
            average_percentage = total_percentage / len(course_grades)
            
            # Get letter grade for average
            from utils.helpers import calculate_grade_letter
            average_letter = calculate_grade_letter(average_percentage)
            
            course_averages.append({
                "course_id": course_id,
                "course_name": course_name,
                "average_percentage": average_percentage,
                "average_letter": average_letter,
                "grades_count": len(course_grades)
            })
        else:
            course_averages.append({
                "course_id": course_id,
                "course_name": course_name,
                "average_percentage": 0,
                "average_letter": "N/A",
                "grades_count": 0
            })
    
    # Calculate overall GPA
    courses_with_grades = [course for course in course_averages if course["grades_count"] > 0]
    
    if courses_with_grades:
        total_percentage = sum(course.get("average_percentage", 0) for course in courses_with_grades)
        overall_average = total_percentage / len(courses_with_grades)
        overall_letter = calculate_grade_letter(overall_average)
        
        print(f"Overall Average: {overall_average:.1f}% ({overall_letter})\n")
    else:
        print("You don't have any grades yet.\n")
    
    # Display course averages
    for course in course_averages:
        course_name = course.get("course_name", "")
        average_percentage = course.get("average_percentage", 0)
        average_letter = course.get("average_letter", "")
        grades_count = course.get("grades_count", 0)
        
        if grades_count > 0:
            print(f"{course_name}: {average_percentage:.1f}% ({average_letter})")
            print(f"  Based on {grades_count} graded assignments")
        else:
            print(f"{course_name}: No grades yet")
        
        print()
    
    input("\nPress Enter to continue...")

def view_attendance_ui(student_id: str) -> None:
    """
    UI for viewing attendance.
    
    Args:
        student_id: ID of the student
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📋 MY ATTENDANCE 📋".center(50))
    print("=" * 50 + "\n")
    
    # Get student's attendance records
    from services.attendance_service import get_student_attendance, calculate_attendance_stats
    
    attendance_records = get_student_attendance(student_id)
    
    if not attendance_records:
        print("No attendance records found.")
        input("\nPress Enter to continue...")
        return
    
    # Calculate attendance statistics
    stats = calculate_attendance_stats(student_id)
    
    print("Attendance Summary:")
    print(f"Total Days: {stats.get('total_days', 0)}")
    print(f"Present: {stats.get('present_days', 0)} ({stats.get('present_percentage', 0):.1f}%)")
    print(f"Absent: {stats.get('absent_days', 0)} ({stats.get('absent_percentage', 0):.1f}%)")
    print(f"Late: {stats.get('late_days', 0)} ({stats.get('late_percentage', 0):.1f}%)")
    print(f"Excused: {stats.get('excused_days', 0)} ({stats.get('excused_percentage', 0):.1f}%)")
    
    print("\nAttendance Records:")
    
    # Sort by date (newest first)
    attendance_records.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    # Group by course
    attendance_by_course = {}
    
    for record in attendance_records:
        course_name = record.get("course_name", "")
        
        if course_name not in attendance_by_course:
            attendance_by_course[course_name] = []
        
        attendance_by_course[course_name].append(record)
    
    # Display attendance by course
    for course_name, records in attendance_by_course.items():
        print(f"\n{course_name}:")
        
        for record in records:
            date = record.get("date", "")
            status = record.get("status", "").upper()
            
            print(f"  {date}: {status}")
    
    input("\nPress Enter to continue...")

def submit_assignment_ui(student_id: str) -> None:
    """
    UI for submitting assignments.
    
    Args:
        student_id: ID of the student
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📤 SUBMIT ASSIGNMENT 📤".center(50))
    print("=" * 50 + "\n")
    
    # Get student's courses
    student_courses = get_student_courses(student_id)
    
    if not student_courses:
        print("You are not enrolled in any courses.")
        input("\nPress Enter to continue...")
        return
    
    # Get assignments for these courses
    assignments = get_data('assignments')
    
    # Filter assignments that are active and not already submitted
    submissions = get_data('submissions')
    
    available_assignments = []
    
    for assignment_id, assignment in assignments.items():
        if assignment.get("course_id") in [course.get("id") for course in student_courses]:
            if assignment.get("status") == "active":
                # Check if already submitted
                is_submitted = False
                for submission in submissions.values():
                    if (submission.get("assignment_id") == assignment_id and 
                        submission.get("student_id") == student_id):
                        is_submitted = True
                        break
                
                if not is_submitted:
                    available_assignments.append({
                        "id": assignment_id,
                        **assignment
                    })
    
    if not available_assignments:
        print("You don't have any assignments to submit.")
        input("\nPress Enter to continue...")
        return
    
    # Sort by due date
    available_assignments.sort(key=lambda x: x.get("due_date", ""))
    
    # Display assignments
    print("Select an assignment to submit:")
    
    for i, assignment in enumerate(available_assignments, 1):
        title = assignment.get("title", "")
        due_date = assignment.get("due_date", "")
        
        # Get course name
        course_id = assignment.get("course_id", "")
        course_name = "Unknown Course"
        
        for course in student_courses:
            if course.get("id") == course_id:
                course_name = course.get("name", "")
                break
        
        print(f"{i}. {title}")
        print(f"   Course: {course_name}")
        print(f"   Due Date: {due_date}")
        print()
    
    print(f"\n{MENU_BACK}. Back")
    
    choice = input("\nEnter your choice: ")
    
    if choice == MENU_BACK:
        return
    
    try:
        assignment_idx = int(choice) - 1
        if 0 <= assignment_idx < len(available_assignments):
            submit_assignment(student_id, available_assignments[assignment_idx])
        else:
            print("\n❌ Invalid choice.")
            input("\nPress Enter to continue...")
    except ValueError:
        print("\n❌ Invalid choice. Please enter a number.")
        input("\nPress Enter to continue...")

def submit_assignment(student_id: str, assignment: Dict[str, Any]) -> None:
    """
    Submit an assignment.
    
    Args:
        student_id: ID of the student
        assignment: Assignment data dictionary
    """
    assignment_id = assignment.get("id", "")
    title = assignment.get("title", "")
    
    clear_screen()
    print("\n" + "=" * 50)
    print(f"📤 SUBMIT: {title} 📤".center(50))
    print("=" * 50 + "\n")
    
    # Get submission details
    print("Enter submission details:\n")
    
    content = input("Submission Content: ")
    comments = input("Comments (optional): ")
    
    # Check if submission is late
    today = datetime.now().strftime("%Y-%m-%d")
    due_date = assignment.get("due_date", "")
    is_late = today > due_date
    
    # Create submission
    submissions = get_data('submissions')
    submission_id = f"SUB{len(submissions) + 1:04d}"
    
    submissions[submission_id] = {
        "assignment_id": assignment_id,
        "student_id": student_id,
        "content": content,
        "comments": comments,
        "submitted_at": datetime.now().isoformat(),
        "is_late": is_late,
        "status": "submitted"
    }
    
    save_data('submissions', submissions)
    
    if is_late:
        print("\n⚠️ This submission is late.")
    
    print("\n✅ Assignment submitted successfully.")
    input("\nPress Enter to continue...")

def view_course_materials_ui(student_id: str) -> None:
    """
    UI for viewing course materials.
    
    Args:
        student_id: ID of the student
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📚 COURSE MATERIALS 📚".center(50))
    print("=" * 50 + "\n")
    
    # Get student's courses
    student_courses = get_student_courses(student_id)
    
    if not student_courses:
        print("You are not enrolled in any courses.")
        input("\nPress Enter to continue...")
        return
    
    # Display courses
    print("Select a course:")
    for i, course in enumerate(student_courses, 1):
        print(f"{i}. {course.get('name', '')} ({course.get('code', '')})")
    
    print(f"\n{MENU_BACK}. Back")
    
    choice = input("\nEnter your choice: ")
    
    if choice == MENU_BACK:
        return
    
    try:
        course_idx = int(choice) - 1
        if 0 <= course_idx < len(student_courses):
            view_course_materials(student_courses[course_idx])
        else:
            print("\n❌ Invalid choice.")
            input("\nPress Enter to continue...")
    except ValueError:
        print("\n❌ Invalid choice. Please enter a number.")
        input("\nPress Enter to continue...")

def view_course_materials(course: Dict[str, Any]) -> None:
    """
    View materials for a specific course.
    
    Args:
        course: Course data dictionary
    """
    course_id = course.get("id", "")
    course_name = course.get("name", "")
    
    clear_screen()
    print("\n" + "=" * 50)
    print(f"📚 MATERIALS: {course_name} 📚".center(50))
    print("=" * 50 + "\n")
    
    # Get course materials
    materials = get_data('materials')
    
    course_materials = []
    for material_id, material in materials.items():
        if material.get("course_id") == course_id:
            course_materials.append({
                "id": material_id,
                **material
            })
    
    if not course_materials:
        print("No materials available for this course.")
        input("\nPress Enter to continue...")
        return
    
    # Sort by uploaded_at
    course_materials.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
    
    # Group by type
    materials_by_type = {}
    
    for material in course_materials:
        material_type = material.get("type", "Other")
        
        if material_type not in materials_by_type:
            materials_by_type[material_type] = []
        
        materials_by_type[material_type].append(material)
    
    # Display materials by type
    for material_type, type_materials in materials_by_type.items():
        print(f"\n{material_type}:")
        
        for i, material in enumerate(type_materials, 1):
            title = material.get("title", "")
            uploaded_at = material.get("uploaded_at", "")
            
            print(f"{i}. {title}")
            print(f"   Uploaded: {uploaded_at}")
        
        print()
    
    # Option to view material details
    material_type = input("\nEnter material type to view (or 0 to return): ")
    
    if material_type == "0":
        return
    
    if material_type in materials_by_type:
        clear_screen()
        print("\n" + "=" * 50)
        print(f"📚 {material_type.upper()} 📚".center(50))
        print("=" * 50 + "\n")
        
        type_materials = materials_by_type[material_type]
        
        for i, material in enumerate(type_materials, 1):
            title = material.get("title", "")
            uploaded_at = material.get("uploaded_at", "")
            
            print(f"{i}. {title}")
            print(f"   Uploaded: {uploaded_at}")
        
        material_idx = input("\nEnter number to view details (or 0 to return): ")
        
        try:
            material_idx = int(material_idx)
            if 1 <= material_idx <= len(type_materials):
                display_material_details(type_materials[material_idx - 1])
        except ValueError:
            pass
    else:
        print("\n❌ Invalid material type.")
        input("\nPress Enter to continue...")

def display_material_details(material: Dict[str, Any]) -> None:
    """
    Display detailed information about a course material.
    
    Args:
        material: Material data dictionary
    """
    clear_screen()
    print("\n" + "=" * 50)
    print(f"📄 MATERIAL DETAILS 📄".center(50))
    print("=" * 50 + "\n")
    
    title = material.get("title", "")
    description = material.get("description", "")
    content = material.get("content", "")
    material_type = material.get("type", "")
    uploaded_at = material.get("uploaded_at", "")
    
    # Get uploader information
    uploader_id = material.get("uploaded_by", "")
    uploader_name = "Unknown"
    
    if uploader_id:
        users = get_data('users')
        for username, user in users.items():
            if user.get("id") == uploader_id:
                uploader_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                if not uploader_name:
                    uploader_name = username
                break
    
    print(f"Title: {title}")
    print(f"Type: {material_type}")
    print(f"Uploaded by: {uploader_name}")
    print(f"Date: {uploaded_at}\n")
    print(f"Description: {description}\n")
    print(f"Content:\n{content}")
    
    input("\nPress Enter to continue...")

def view_announcements_ui(role: str) -> None:
    """
    UI for viewing school announcements.
    
    Args:
        role: Role of the user
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📢 SCHOOL ANNOUNCEMENTS 📢".center(50))
    print("=" * 50 + "\n")
    
    # Get announcements
    announcements = get_data('announcements')
    
    # Filter announcements by role
    visible_announcements = []
    for announcement_id, announcement in announcements.items():
        audience = announcement.get("audience", [])
        if "all" in audience or role in audience:
            visible_announcements.append({
                "id": announcement_id,
                **announcement
            })
    
    if not visible_announcements:
        print("No announcements available.")
        input("\nPress Enter to continue...")
        return
    
    # Sort by created_at (newest first)
    visible_announcements.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Display announcements
    for i, announcement in enumerate(visible_announcements, 1):
        title = announcement.get("title", "")
        created_at = announcement.get("created_at", "")
        is_important = announcement.get("is_important", False)
        
        if is_important:
            print(f"{i}. 🔴 {title} (IMPORTANT)")
        else:
            print(f"{i}. {title}")
        
        print(f"   Posted: {created_at}")
        print()
    
    # Option to view announcement details
    announcement_idx = input("\nEnter number to view details (or 0 to return): ")
    try:
        announcement_idx = int(announcement_idx)
        if 1 <= announcement_idx <= len(visible_announcements):
            display_announcement_details(visible_announcements[announcement_idx - 1])
    except ValueError:
        pass

def display_announcement_details(announcement: Dict[str, Any]) -> None:
    """
    Display detailed information about an announcement.
    
    Args:
        announcement: Announcement data dictionary
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📢 ANNOUNCEMENT DETAILS 📢".center(50))
    print("=" * 50 + "\n")
    
    title = announcement.get("title", "")
    content = announcement.get("content", "")
    created_at = announcement.get("created_at", "")
    is_important = announcement.get("is_important", False)
    
    # Get author information
    author_id = announcement.get("author_id", "")
    author_name = "Unknown"
    
    if author_id:
        users = get_data('users')
        for username, user in users.items():
            if user.get("id") == author_id:
                author_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                if not author_name:
                    author_name = username
                break
    
    if is_important:
        print(f"🔴 {title} (IMPORTANT)")
    else:
        print(f"{title}")
    
    print(f"Posted by: {author_name}")
    print(f"Date: {created_at}\n")
    print(f"{content}")
    
    input("\nPress Enter to continue...")
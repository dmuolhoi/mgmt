"""
Teacher dashboard for the School Management System
"""
import os
from datetime import datetime
from typing import List, Dict, Any
from utils.helpers import clear_screen, get_user_by_id
from utils.constants import USER_ROLES, MENU_BACK, MENU_LOGOUT, ATTENDANCE_STATUS
from storage.datastore import get_data, save_data
from services.event_service import get_upcoming_events
from services.teacher_service import get_teacher_courses
from services.attendance_service import mark_attendance, update_attendance, get_course_attendance

def teacher_dashboard(teacher_id: str) -> None:
    """
    Display the teacher dashboard.
    
    Args:
        teacher_id: The ID of the teacher user
    """
    teacher = get_user_by_id(teacher_id)
    if not teacher or teacher["role"] != USER_ROLES.TEACHER:
        print("❌ Access denied: Teacher privileges required")
        return
    
    username = teacher["username"]
    
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print(f"👩‍🏫 TEACHER DASHBOARD: {username} 👨‍🏫".center(50))
        print("=" * 50)
        
        # Show upcoming events
        print("\n📅 Upcoming Events:")
        upcoming_events = get_upcoming_events(USER_ROLES.TEACHER, 3)
        if upcoming_events:
            for event in upcoming_events:
                print(f"- {event['title']} ({event['start_date']})")
        else:
            print("- No upcoming events")
        
        print("\n" + "-" * 50)
        print("1. Mark Attendance")
        print("2. Assign Grades")
        print("3. Manage Assignments")
        print("4. View Class List")
        print("5. Communicate with Parents")
        print("6. View School Announcements")
        print(f"\n{MENU_LOGOUT}. Logout")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            mark_attendance_ui(teacher_id)
        elif choice == "2":
            assign_grades_ui(teacher_id)
        elif choice == "3":
            manage_assignments_ui(teacher_id)
        elif choice == "4":
            view_class_list_ui(teacher_id)
        elif choice == "5":
            communicate_with_parents_ui(teacher_id)
        elif choice == "6":
            view_announcements_ui(USER_ROLES.TEACHER)
        elif choice == MENU_LOGOUT:
            print("\nLogging out...")
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

def mark_attendance_ui(teacher_id: str) -> None:
    """
    UI for marking attendance.
    
    Args:
        teacher_id: ID of the teacher
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📋 MARK ATTENDANCE 📋".center(50))
    print("=" * 50 + "\n")
    
    # Get teacher's courses
    teacher_courses = get_teacher_courses(teacher_id)
    
    if not teacher_courses:
        print("You don't have any assigned courses.")
        input("\nPress Enter to continue...")
        return
    
    # Display courses
    print("Select a course:")
    for i, course in enumerate(teacher_courses, 1):
        print(f"{i}. {course.get('name', '')} ({course.get('code', '')})")
    
    print(f"\n{MENU_BACK}. Back")
    
    choice = input("\nEnter your choice: ")
    
    if choice == MENU_BACK:
        return
    
    try:
        course_idx = int(choice) - 1
        if 0 <= course_idx < len(teacher_courses):
            selected_course = teacher_courses[course_idx]
            course_id = selected_course.get("id", "")
            
            # Get date for attendance
            date_input = input("\nEnter date (YYYY-MM-DD) or leave blank for today: ")
            if not date_input:
                date = datetime.now().strftime("%Y-%m-%d")
            else:
                try:
                    # Validate date format
                    datetime.strptime(date_input, "%Y-%m-%d")
                    date = date_input
                except ValueError:
                    print("\n❌ Invalid date format. Please use YYYY-MM-DD.")
                    input("\nPress Enter to continue...")
                    return
            
            # Check if attendance already exists for this date
            attendance = get_data('attendance')
            attendance_key = f"{course_id}_{date}"
            
            if attendance_key in attendance:
                print(f"\nAttendance for {selected_course.get('name', '')} on {date} already exists.")
                print("\nDo you want to update it?")
                print("1. Yes")
                print("2. No")
                
                update_choice = input("\nEnter your choice: ")
                
                if update_choice != "1":
                    return
                
                existing_attendance = attendance[attendance_key]
                take_attendance(teacher_id, course_id, date, existing_attendance.get("students", []))
            else:
                take_attendance(teacher_id, course_id, date)
        else:
            print("\n❌ Invalid choice.")
            input("\nPress Enter to continue...")
    except ValueError:
        print("\n❌ Invalid choice. Please enter a number.")
        input("\nPress Enter to continue...")

def take_attendance(teacher_id: str, course_id: str, date: str, 
                   existing_students: List[Dict[str, Any]] = None) -> None:
    """
    Take or update attendance for a class.
    
    Args:
        teacher_id: ID of the teacher
        course_id: ID of the course
        date: Date for attendance
        existing_students: Optional list of existing student attendance records
    """
    # Get all students in the course
    courses = get_data('courses')
    students = get_data('students')
    
    if course_id not in courses:
        print("\n❌ Course not found.")
        input("\nPress Enter to continue...")
        return
    
    student_ids = courses[course_id].get("students", [])
    
    if not student_ids:
        print("\nNo students enrolled in this course.")
        input("\nPress Enter to continue...")
        return
    
    # Create student attendance records
    attendance_data = []
    
    clear_screen()
    print("\n" + "=" * 50)
    print(f"📋 ATTENDANCE: {courses[course_id].get('name', '')} - {date} 📋".center(50))
    print("=" * 50 + "\n")
    
    print("Mark attendance for each student:")
    print("P - Present, A - Absent, L - Late, E - Excused\n")
    
    # Create a dict of existing attendance by student_id for quick lookup
    existing_by_student = {}
    if existing_students:
        for record in existing_students:
            existing_by_student[record.get("student_id")] = record.get("status")
    
    # Process each student
    for student_id in student_ids:
        if student_id in students:
            student = students[student_id]
            name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
            
            # Get existing status if available
            existing_status = existing_by_student.get(student_id, "")
            status_prompt = f" [Current: {existing_status.upper()}]" if existing_status else ""
            
            while True:
                status_input = input(f"{name}{status_prompt}: ").upper()
                
                if status_input == "P":
                    status = ATTENDANCE_STATUS.PRESENT
                    break
                elif status_input == "A":
                    status = ATTENDANCE_STATUS.ABSENT
                    break
                elif status_input == "L":
                    status = ATTENDANCE_STATUS.LATE
                    break
                elif status_input == "E":
                    status = ATTENDANCE_STATUS.EXCUSED
                    break
                elif not status_input and existing_status:
                    status = existing_status
                    break
                else:
                    print("❌ Invalid input. Use P, A, L, or E.")
            
            # Add to attendance data
            attendance_data.append({
                "student_id": student_id,
                "status": status
            })
    
    # Confirm submission
    print("\nReview attendance:")
    for record in attendance_data:
        student_id = record.get("student_id")
        status = record.get("status")
        
        if student_id in students:
            student = students[student_id]
            name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
            print(f"- {name}: {status.upper()}")
    
    confirm = input("\nSubmit attendance? (y/n): ")
    
    if confirm.lower() == 'y':
        if existing_students:
            # Update existing attendance
            success, message = update_attendance(teacher_id, course_id, date, attendance_data)
        else:
            # Create new attendance
            success, message = mark_attendance(teacher_id, course_id, date, attendance_data)
        
        print(f"\n{message}")
    else:
        print("\nAttendance submission cancelled.")
    
    input("\nPress Enter to continue...")

def assign_grades_ui(teacher_id: str) -> None:
    """
    UI for assigning grades.
    
    Args:
        teacher_id: ID of the teacher
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📝 ASSIGN GRADES 📝".center(50))
    print("=" * 50 + "\n")
    
    # Get teacher's courses
    teacher_courses = get_teacher_courses(teacher_id)
    
    if not teacher_courses:
        print("You don't have any assigned courses.")
        input("\nPress Enter to continue...")
        return
    
    # Display courses
    print("Select a course:")
    for i, course in enumerate(teacher_courses, 1):
        print(f"{i}. {course.get('name', '')} ({course.get('code', '')})")
    
    print(f"\n{MENU_BACK}. Back")
    
    choice = input("\nEnter your choice: ")
    
    if choice == MENU_BACK:
        return
    
    try:
        course_idx = int(choice) - 1
        if 0 <= course_idx < len(teacher_courses):
            selected_course = teacher_courses[course_idx]
            course_id = selected_course.get("id", "")
            
            # Get assignment type
            print("\nSelect assignment type:")
            print("1. Quiz")
            print("2. Test")
            print("3. Homework")
            print("4. Project")
            print("5. Exam")
            print("6. Other")
            
            type_choice = input("\nEnter your choice: ")
            
            assignment_types = {
                "1": "Quiz",
                "2": "Test",
                "3": "Homework",
                "4": "Project",
                "5": "Exam",
                "6": "Other"
            }
            
            if type_choice not in assignment_types:
                print("\n❌ Invalid choice.")
                input("\nPress Enter to continue...")
                return
            
            assignment_type = assignment_types[type_choice]
            
            # Get assignment name
            assignment_name = input("\nEnter assignment name: ")
            if not assignment_name:
                print("\n❌ Assignment name is required.")
                input("\nPress Enter to continue...")
                return
            
            # Get max points
            try:
                max_points = float(input("\nEnter maximum points: "))
            except ValueError:
                print("\n❌ Invalid input for maximum points.")
                input("\nPress Enter to continue...")
                return
            
            # Get grade date
            date_input = input("\nEnter grade date (YYYY-MM-DD) or leave blank for today: ")
            if not date_input:
                date = datetime.now().strftime("%Y-%m-%d")
            else:
                try:
                    # Validate date format
                    datetime.strptime(date_input, "%Y-%m-%d")
                    date = date_input
                except ValueError:
                    print("\n❌ Invalid date format. Please use YYYY-MM-DD.")
                    input("\nPress Enter to continue...")
                    return
            
            # Process grades for students
            enter_grades(
                teacher_id, 
                course_id, 
                assignment_type, 
                assignment_name, 
                max_points, 
                date
            )
        else:
            print("\n❌ Invalid choice.")
            input("\nPress Enter to continue...")
    except ValueError:
        print("\n❌ Invalid choice. Please enter a number.")
        input("\nPress Enter to continue...")

def enter_grades(teacher_id: str, course_id: str, assignment_type: str, 
                assignment_name: str, max_points: float, date: str) -> None:
    """
    Enter grades for students in a course.
    
    Args:
        teacher_id: ID of the teacher
        course_id: ID of the course
        assignment_type: Type of assignment
        assignment_name: Name of the assignment
        max_points: Maximum points possible
        date: Date for the grades
    """
    # Get all students in the course
    courses = get_data('courses')
    students = get_data('students')
    
    if course_id not in courses:
        print("\n❌ Course not found.")
        input("\nPress Enter to continue...")
        return
    
    student_ids = courses[course_id].get("students", [])
    
    if not student_ids:
        print("\nNo students enrolled in this course.")
        input("\nPress Enter to continue...")
        return
    
    # Create assignment entry
    assignments = get_data('assignments')
    assignment_id = f"ASN{len(assignments) + 1:04d}"
    
    assignments[assignment_id] = {
        "course_id": course_id,
        "name": assignment_name,
        "type": assignment_type,
        "max_points": max_points,
        "date": date,
        "created_by": teacher_id,
        "created_at": datetime.now().isoformat()
    }
    
    save_data('assignments', assignments)
    
    # Process student grades
    grades = get_data('grades')
    student_grades = []
    
    clear_screen()
    print("\n" + "=" * 50)
    print(f"📝 GRADES: {assignment_name} 📝".center(50))
    print("=" * 50 + "\n")
    
    print(f"Course: {courses[course_id].get('name', '')}")
    print(f"Type: {assignment_type}")
    print(f"Max Points: {max_points}")
    print(f"Date: {date}\n")
    
    print("Enter grades for each student (leave blank to skip):\n")
    
    # Process each student
    for student_id in student_ids:
        if student_id in students:
            student = students[student_id]
            name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
            
            while True:
                try:
                    points_input = input(f"{name}: ")
                    
                    if not points_input:
                        # Skip this student
                        break
                    
                    points = float(points_input)
                    
                    if points < 0 or points > max_points:
                        print(f"❌ Points must be between 0 and {max_points}.")
                        continue
                    
                    # Calculate percentage
                    percentage = (points / max_points) * 100
                    
                    # Get letter grade using helper function
                    from utils.helpers import calculate_grade_letter
                    letter_grade = calculate_grade_letter(percentage)
                    
                    # Create grade record
                    grade_id = f"GRD{len(grades) + 1:04d}"
                    grades[grade_id] = {
                        "student_id": student_id,
                        "course_id": course_id,
                        "assignment_id": assignment_id,
                        "points": points,
                        "max_points": max_points,
                        "percentage": percentage,
                        "letter_grade": letter_grade,
                        "graded_by": teacher_id,
                        "graded_at": datetime.now().isoformat()
                    }
                    
                    # Add to student grades for display
                    student_grades.append({
                        "student_name": name,
                        "points": points,
                        "percentage": percentage,
                        "letter_grade": letter_grade
                    })
                    
                    break
                except ValueError:
                    print("❌ Invalid input. Please enter a number.")
    
    # Save grades
    save_data('grades', grades)
    
    # Show summary
    print("\nGrades Summary:")
    for grade in student_grades:
        print(f"- {grade['student_name']}: {grade['points']} ({grade['percentage']:.1f}%) - {grade['letter_grade']}")
    
    print(f"\n✅ Grades for {assignment_name} recorded successfully.")
    input("\nPress Enter to continue...")

def manage_assignments_ui(teacher_id: str) -> None:
    """
    UI for managing assignments.
    
    Args:
        teacher_id: ID of the teacher
    """
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print("📚 MANAGE ASSIGNMENTS 📚".center(50))
        print("=" * 50 + "\n")
        
        print("1. Create New Assignment")
        print("2. View Existing Assignments")
        print("3. Grade Submitted Assignments")
        print(f"\n{MENU_BACK}. Back")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            create_assignment_ui(teacher_id)
        elif choice == "2":
            view_assignments_ui(teacher_id)
        elif choice == "3":
            grade_assignments_ui(teacher_id)
        elif choice == MENU_BACK:
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

def create_assignment_ui(teacher_id: str) -> None:
    """
    UI for creating a new assignment.
    
    Args:
        teacher_id: ID of the teacher
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📝 CREATE ASSIGNMENT 📝".center(50))
    print("=" * 50 + "\n")
    
    # Get teacher's courses
    teacher_courses = get_teacher_courses(teacher_id)
    
    if not teacher_courses:
        print("You don't have any assigned courses.")
        input("\nPress Enter to continue...")
        return
    
    # Display courses
    print("Select a course:")
    for i, course in enumerate(teacher_courses, 1):
        print(f"{i}. {course.get('name', '')} ({course.get('code', '')})")
    
    print(f"\n{MENU_BACK}. Back")
    
    choice = input("\nEnter your choice: ")
    
    if choice == MENU_BACK:
        return
    
    try:
        course_idx = int(choice) - 1
        if 0 <= course_idx < len(teacher_courses):
            selected_course = teacher_courses[course_idx]
            course_id = selected_course.get("id", "")
            
            # Get assignment details
            title = input("\nAssignment Title: ")
            description = input("Assignment Description: ")
            
            # Get assignment type
            print("\nSelect assignment type:")
            print("1. Quiz")
            print("2. Test")
            print("3. Homework")
            print("4. Project")
            print("5. Exam")
            print("6. Other")
            
            type_choice = input("\nEnter your choice: ")
            
            assignment_types = {
                "1": "Quiz",
                "2": "Test",
                "3": "Homework",
                "4": "Project",
                "5": "Exam",
                "6": "Other"
            }
            
            if type_choice not in assignment_types:
                print("\n❌ Invalid choice.")
                input("\nPress Enter to continue...")
                return
            
            assignment_type = assignment_types[type_choice]
            
            # Get max points
            try:
                max_points = float(input("\nMaximum Points: "))
            except ValueError:
                print("\n❌ Invalid input for maximum points.")
                input("\nPress Enter to continue...")
                return
            
            # Get due date
            due_date = input("Due Date (YYYY-MM-DD): ")
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                print("\n❌ Invalid date format. Please use YYYY-MM-DD.")
                input("\nPress Enter to continue...")
                return
            
            # Create assignment
            assignments = get_data('assignments')
            assignment_id = f"ASN{len(assignments) + 1:04d}"
            
            assignments[assignment_id] = {
                "title": title,
                "description": description,
                "type": assignment_type,
                "course_id": course_id,
                "max_points": max_points,
                "due_date": due_date,
                "created_by": teacher_id,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            save_data('assignments', assignments)
            
            print(f"\n✅ Assignment '{title}' created successfully.")
        else:
            print("\n❌ Invalid choice.")
    except ValueError:
        print("\n❌ Invalid choice. Please enter a number.")
    
    input("\nPress Enter to continue...")

def view_assignments_ui(teacher_id: str) -> None:
    """
    UI for viewing existing assignments.
    
    Args:
        teacher_id: ID of the teacher
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📚 VIEW ASSIGNMENTS 📚".center(50))
    print("=" * 50 + "\n")
    
    # Get teacher's courses
    teacher_courses = get_teacher_courses(teacher_id)
    course_ids = [course.get("id", "") for course in teacher_courses]
    
    # Get assignments for these courses
    assignments = get_data('assignments')
    
    teacher_assignments = []
    for assignment_id, assignment in assignments.items():
        if assignment.get("course_id") in course_ids:
            teacher_assignments.append({**assignment, "id": assignment_id})
    
    if not teacher_assignments:
        print("You haven't created any assignments yet.")
        input("\nPress Enter to continue...")
        return
    
    # Sort by due date
    teacher_assignments.sort(key=lambda x: x.get("due_date", ""))
    
    # Display assignments
    for i, assignment in enumerate(teacher_assignments, 1):
        title = assignment.get("title", "")
        course_id = assignment.get("course_id", "")
        due_date = assignment.get("due_date", "")
        
        # Get course name
        courses = get_data('courses')
        course_name = "Unknown Course"
        if course_id in courses:
            course_name = courses[course_id].get("name", "Unknown Course")
        
        print(f"{i}. {title}")
        print(f"   Course: {course_name}")
        print(f"   Due Date: {due_date}")
        print(f"   Status: {assignment.get('status', 'active')}")
        print()
    
    # Option to view assignment details
    assignment_idx = input("\nEnter number to view details (or 0 to return): ")
    try:
        assignment_idx = int(assignment_idx)
        if 1 <= assignment_idx <= len(teacher_assignments):
            display_assignment_details(teacher_assignments[assignment_idx - 1])
    except ValueError:
        pass

def display_assignment_details(assignment: Dict[str, Any]) -> None:
    """
    Display detailed information about an assignment.
    
    Args:
        assignment: Assignment data dictionary
    """
    clear_screen()
    print("\n" + "=" * 50)
    print(f"📝 ASSIGNMENT DETAILS 📝".center(50))
    print("=" * 50 + "\n")
    
    title = assignment.get("title", "")
    description = assignment.get("description", "")
    assignment_type = assignment.get("type", "")
    course_id = assignment.get("course_id", "")
    max_points = assignment.get("max_points", 0)
    due_date = assignment.get("due_date", "")
    status = assignment.get("status", "active")
    
    # Get course name
    courses = get_data('courses')
    course_name = "Unknown Course"
    if course_id in courses:
        course_name = courses[course_id].get("name", "Unknown Course")
    
    print(f"Title: {title}")
    print(f"Description: {description}")
    print(f"Type: {assignment_type}")
    print(f"Course: {course_name}")
    print(f"Maximum Points: {max_points}")
    print(f"Due Date: {due_date}")
    print(f"Status: {status}")
    
    # Get submission statistics
    submissions = get_data('submissions')
    
    assignment_submissions = []
    for submission_id, submission in submissions.items():
        if submission.get("assignment_id") == assignment.get("id"):
            assignment_submissions.append(submission)
    
    total_students = len(courses.get(course_id, {}).get("students", []))
    submitted_count = len(assignment_submissions)
    
    print(f"\nSubmissions: {submitted_count}/{total_students}")
    
    input("\nPress Enter to continue...")

def grade_assignments_ui(teacher_id: str) -> None:
    """
    UI for grading submitted assignments.
    
    Args:
        teacher_id: ID of the teacher
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("🔍 GRADE ASSIGNMENTS 🔍".center(50))
    print("=" * 50 + "\n")
    
    # Get teacher's courses
    teacher_courses = get_teacher_courses(teacher_id)
    course_ids = [course.get("id", "") for course in teacher_courses]
    
    # Get assignments for these courses
    assignments = get_data('assignments')
    
    teacher_assignments = []
    for assignment_id, assignment in assignments.items():
        if assignment.get("course_id") in course_ids:
            teacher_assignments.append({**assignment, "id": assignment_id})
    
    if not teacher_assignments:
        print("You haven't created any assignments yet.")
        input("\nPress Enter to continue...")
        return
    
    # Sort by due date
    teacher_assignments.sort(key=lambda x: x.get("due_date", ""))
    
    # Display assignments
    print("Select an assignment to grade:")
    for i, assignment in enumerate(teacher_assignments, 1):
        title = assignment.get("title", "")
        course_id = assignment.get("course_id", "")
        
        # Get course name
        courses = get_data('courses')
        course_name = "Unknown Course"
        if course_id in courses:
            course_name = courses[course_id].get("name", "Unknown Course")
        
        print(f"{i}. {title} ({course_name})")
    
    print(f"\n{MENU_BACK}. Back")
    
    choice = input("\nEnter your choice: ")
    
    if choice == MENU_BACK:
        return
    
    try:
        assignment_idx = int(choice) - 1
        if 0 <= assignment_idx < len(teacher_assignments):
            grade_assignment(teacher_id, teacher_assignments[assignment_idx])
        else:
            print("\n❌ Invalid choice.")
            input("\nPress Enter to continue...")
    except ValueError:
        print("\n❌ Invalid choice. Please enter a number.")
        input("\nPress Enter to continue...")

def grade_assignment(teacher_id: str, assignment: Dict[str, Any]) -> None:
    """
    Grade submitted assignments.
    
    Args:
        teacher_id: ID of the teacher
        assignment: Assignment data dictionary
    """
    assignment_id = assignment.get("id", "")
    course_id = assignment.get("course_id", "")
    max_points = assignment.get("max_points", 0)
    
    # Get course students
    courses = get_data('courses')
    students = get_data('students')
    
    if course_id not in courses:
        print("\n❌ Course not found.")
        input("\nPress Enter to continue...")
        return
    
    student_ids = courses[course_id].get("students", [])
    
    if not student_ids:
        print("\nNo students enrolled in this course.")
        input("\nPress Enter to continue...")
        return
    
    # Get submissions for this assignment
    submissions = get_data('submissions')
    
    assignment_submissions = {}
    for submission_id, submission in submissions.items():
        if submission.get("assignment_id") == assignment_id:
            student_id = submission.get("student_id")
            assignment_submissions[student_id] = {
                "id": submission_id,
                **submission
            }
    
    # Process grades
    grades = get_data('grades')
    
    clear_screen()
    print("\n" + "=" * 50)
    print(f"🔍 GRADE: {assignment.get('title', '')} 🔍".center(50))
    print("=" * 50 + "\n")
    
    print(f"Course: {courses[course_id].get('name', '')}")
    print(f"Maximum Points: {max_points}\n")
    
    print("Enter grades for submitted assignments (leave blank to skip):\n")
    
    # Process each student
    for student_id in student_ids:
        if student_id in students:
            student = students[student_id]
            name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
            
            if student_id in assignment_submissions:
                submission = assignment_submissions[student_id]
                submission_date = submission.get("submitted_at", "")
                
                # Check if already graded
                is_graded = False
                for grade_id, grade in grades.items():
                    if (grade.get("assignment_id") == assignment_id and 
                        grade.get("student_id") == student_id):
                        is_graded = True
                        break
                
                if is_graded:
                    print(f"{name}: Already graded")
                    continue
                
                print(f"{name} (Submitted: {submission_date})")
                
                while True:
                    try:
                        points_input = input(f"  Points (max {max_points}): ")
                        
                        if not points_input:
                            # Skip this student
                            break
                        
                        points = float(points_input)
                        
                        if points < 0 or points > max_points:
                            print(f"  ❌ Points must be between 0 and {max_points}.")
                            continue
                        
                        comments = input("  Comments: ")
                        
                        # Calculate percentage
                        percentage = (points / max_points) * 100
                        
                        # Get letter grade using helper function
                        from utils.helpers import calculate_grade_letter
                        letter_grade = calculate_grade_letter(percentage)
                        
                        # Create grade record
                        grade_id = f"GRD{len(grades) + 1:04d}"
                        grades[grade_id] = {
                            "student_id": student_id,
                            "course_id": course_id,
                            "assignment_id": assignment_id,
                            "submission_id": submission.get("id"),
                            "points": points,
                            "max_points": max_points,
                            "percentage": percentage,
                            "letter_grade": letter_grade,
                            "comments": comments,
                            "graded_by": teacher_id,
                            "graded_at": datetime.now().isoformat()
                        }
                        
                        # Update submission status
                        submissions[submission.get("id")]["status"] = "graded"
                        submissions[submission.get("id")]["graded_at"] = datetime.now().isoformat()
                        submissions[submission.get("id")]["graded_by"] = teacher_id
                        
                        break
                    except ValueError:
                        print("  ❌ Invalid input. Please enter a number.")
            else:
                print(f"{name}: Not submitted")
    
    # Save grades and updated submissions
    save_data('grades', grades)
    save_data('submissions', submissions)
    
    print(f"\n✅ Grading for {assignment.get('title', '')} completed.")
    input("\nPress Enter to continue...")

def view_class_list_ui(teacher_id: str) -> None:
    """
    UI for viewing class lists.
    
    Args:
        teacher_id: ID of the teacher
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("👥 CLASS LISTS 👥".center(50))
    print("=" * 50 + "\n")
    
    # Get teacher's courses
    teacher_courses = get_teacher_courses(teacher_id)
    
    if not teacher_courses:
        print("You don't have any assigned courses.")
        input("\nPress Enter to continue...")
        return
    
    # Display courses
    print("Select a course:")
    for i, course in enumerate(teacher_courses, 1):
        print(f"{i}. {course.get('name', '')} ({course.get('code', '')})")
    
    print(f"\n{MENU_BACK}. Back")
    
    choice = input("\nEnter your choice: ")
    
    if choice == MENU_BACK:
        return
    
    try:
        course_idx = int(choice) - 1
        if 0 <= course_idx < len(teacher_courses):
            selected_course = teacher_courses[course_idx]
            view_course_students(selected_course)
        else:
            print("\n❌ Invalid choice.")
            input("\nPress Enter to continue...")
    except ValueError:
        print("\n❌ Invalid choice. Please enter a number.")
        input("\nPress Enter to continue...")

def view_course_students(course: Dict[str, Any]) -> None:
    """
    View students enrolled in a course.
    
    Args:
        course: Course data dictionary
    """
    course_id = course.get("id", "")
    
    # Get course students
    courses = get_data('courses')
    students = get_data('students')
    
    if course_id not in courses:
        print("\n❌ Course not found.")
        input("\nPress Enter to continue...")
        return
    
    student_ids = courses[course_id].get("students", [])
    
    if not student_ids:
        print("\nNo students enrolled in this course.")
        input("\nPress Enter to continue...")
        return
    
    clear_screen()
    print("\n" + "=" * 50)
    print(f"👥 CLASS LIST: {course.get('name', '')} 👥".center(50))
    print("=" * 50 + "\n")
    
    # Display students
    print(f"Total Students: {len(student_ids)}\n")
    
    for i, student_id in enumerate(student_ids, 1):
        if student_id in students:
            student = students[student_id]
            name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
            email = student.get("email", "")
            print(f"{i}. {name}")
            print(f"   Email: {email}")
            print()
    
    # Option to view student details
    student_idx = input("\nEnter number to view details (or 0 to return): ")
    try:
        student_idx = int(student_idx)
        if 1 <= student_idx <= len(student_ids):
            student_id = student_ids[student_idx - 1]
            if student_id in students:
                display_student_details(student_id)
    except ValueError:
        pass

def display_student_details(student_id: str) -> None:
    """
    Display detailed information about a student.
    
    Args:
        student_id: ID of the student
    """
    students = get_data('students')
    if student_id not in students:
        print("\n❌ Student not found.")
        input("\nPress Enter to continue...")
        return
    
    student = students[student_id]
    
    clear_screen()
    print("\n" + "=" * 50)
    print(f"👤 STUDENT DETAILS 👤".center(50))
    print("=" * 50 + "\n")
    
    name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
    print(f"Name: {name}")
    print(f"ID: {student_id}")
    print(f"Email: {student.get('email', '')}")
    print(f"Phone: {student.get('phone', '')}")
    print(f"Grade Level: {student.get('grade_level', '')}")
    
    # Get parent information
    parent_id = student.get("parent_id", "")
    if parent_id:
        parents = get_data('parents')
        if parent_id in parents:
            parent = parents[parent_id]
            parent_name = f"{parent.get('first_name', '')} {parent.get('last_name', '')}".strip()
            parent_email = parent.get("email", "")
            parent_phone = parent.get("phone", "")
            
            print("\nParent Information:")
            print(f"Name: {parent_name}")
            print(f"Email: {parent_email}")
            print(f"Phone: {parent_phone}")
    
    # Get attendance statistics
    from services.attendance_service import calculate_attendance_stats
    attendance_stats = calculate_attendance_stats(student_id)
    
    print("\nAttendance Statistics:")
    print(f"Total Days: {attendance_stats.get('total_days', 0)}")
    print(f"Present: {attendance_stats.get('present_days', 0)} ({attendance_stats.get('present_percentage', 0):.1f}%)")
    print(f"Absent: {attendance_stats.get('absent_days', 0)} ({attendance_stats.get('absent_percentage', 0):.1f}%)")
    print(f"Late: {attendance_stats.get('late_days', 0)} ({attendance_stats.get('late_percentage', 0):.1f}%)")
    
    input("\nPress Enter to continue...")

def communicate_with_parents_ui(teacher_id: str) -> None:
    """
    UI for communicating with parents.
    
    Args:
        teacher_id: ID of the teacher
    """
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print("📨 COMMUNICATE WITH PARENTS 📨".center(50))
        print("=" * 50 + "\n")
        
        print("1. Send New Message")
        print("2. View Message History")
        print(f"\n{MENU_BACK}. Back")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            send_parent_message_ui(teacher_id)
        elif choice == "2":
            view_parent_messages_ui(teacher_id)
        elif choice == MENU_BACK:
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

def send_parent_message_ui(teacher_id: str) -> None:
    """
    UI for sending a message to a parent.
    
    Args:
        teacher_id: ID of the teacher
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📤 SEND MESSAGE TO PARENT 📤".center(50))
    print("=" * 50 + "\n")
    
    # Get teacher's students
    teacher_courses = get_teacher_courses(teacher_id)
    course_ids = [course.get("id", "") for course in teacher_courses]
    
    student_ids = set()
    courses = get_data('courses')
    
    for course_id in course_ids:
        if course_id in courses:
            student_ids.update(courses[course_id].get("students", []))
    
    if not student_ids:
        print("You don't have any students.")
        input("\nPress Enter to continue...")
        return
    
    # Get students with parents
    students = get_data('students')
    students_with_parents = []
    
    for student_id in student_ids:
        if student_id in students and students[student_id].get("parent_id"):
            students_with_parents.append({
                "id": student_id,
                **students[student_id]
            })
    
    if not students_with_parents:
        print("None of your students have registered parents.")
        input("\nPress Enter to continue...")
        return
    
    # Display students
    print("Select a student whose parent you want to message:")
    for i, student in enumerate(students_with_parents, 1):
        name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
        print(f"{i}. {name}")
    
    print(f"\n{MENU_BACK}. Back")
    
    choice = input("\nEnter your choice: ")
    
    if choice == MENU_BACK:
        return
    
    try:
        student_idx = int(choice) - 1
        if 0 <= student_idx < len(students_with_parents):
            selected_student = students_with_parents[student_idx]
            student_name = f"{selected_student.get('first_name', '')} {selected_student.get('last_name', '')}".strip()
            parent_id = selected_student.get("parent_id")
            
            # Get parent info
            parents = get_data('parents')
            if parent_id not in parents:
                print("\n❌ Parent information not found.")
                input("\nPress Enter to continue...")
                return
            
            parent = parents[parent_id]
            parent_name = f"{parent.get('first_name', '')} {parent.get('last_name', '')}".strip()
            
            # Get message details
            print(f"\nSending message to parent of {student_name}")
            print(f"Parent: {parent_name}")
            
            subject = input("\nSubject: ")
            message = input("Message: ")
            
            # Send the message
            messages = get_data('messages')
            message_id = f"MSG{len(messages) + 1:04d}"
            
            messages[message_id] = {
                "from_id": teacher_id,
                "to_id": parent_id,
                "student_id": selected_student.get("id"),
                "subject": subject,
                "message": message,
                "sent_at": datetime.now().isoformat(),
                "read": False
            }
            
            save_data('messages', messages)
            
            print("\n✅ Message sent successfully.")
        else:
            print("\n❌ Invalid choice.")
    except ValueError:
        print("\n❌ Invalid choice. Please enter a number.")
    
    input("\nPress Enter to continue...")

def view_parent_messages_ui(teacher_id: str) -> None:
    """
    UI for viewing message history with parents.
    
    Args:
        teacher_id: ID of the teacher
    """
    clear_screen()
    print("\n" + "=" * 50)
    print("📬 MESSAGE HISTORY 📬".center(50))
    print("=" * 50 + "\n")
    
    # Get teacher's messages
    messages = get_data('messages')
    
    teacher_messages = []
    for message_id, message in messages.items():
        if message.get("from_id") == teacher_id or message.get("to_id") == teacher_id:
            teacher_messages.append({
                "id": message_id,
                **message
            })
    
    if not teacher_messages:
        print("You don't have any messages.")
        input("\nPress Enter to continue...")
        return
    
    # Sort by sent_at (newest first)
    teacher_messages.sort(key=lambda x: x.get("sent_at", ""), reverse=True)
    
    # Group by conversation
    conversations = {}
    
    for message in teacher_messages:
        from_id = message.get("from_id")
        to_id = message.get("to_id")
        student_id = message.get("student_id")
        
        if from_id == teacher_id:
            parent_id = to_id
        else:
            parent_id = from_id
        
        if student_id not in conversations:
            conversations[student_id] = []
        
        conversations[student_id].append(message)
    
    # Display conversations
    print("Select a conversation:")
    
    students = get_data('students')
    parents = get_data('parents')
    
    i = 1
    conversation_map = {}
    
    for student_id, msgs in conversations.items():
        # Get student and parent names
        student_name = "Unknown Student"
        parent_name = "Unknown Parent"
        
        if student_id in students:
            student = students[student_id]
            student_name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
            
            parent_id = student.get("parent_id")
            if parent_id in parents:
                parent = parents[parent_id]
                parent_name = f"{parent.get('first_name', '')} {parent.get('last_name', '')}".strip()
        
        latest_message = msgs[0]
        sent_at = latest_message.get("sent_at", "")
        unread = sum(1 for msg in msgs if msg.get("to_id") == teacher_id and not msg.get("read", False))
        
        print(f"{i}. Conversation with parent of {student_name}")
        print(f"   Latest message: {sent_at}")
        if unread > 0:
            print(f"   Unread messages: {unread}")
        print()
        
        conversation_map[i] = student_id
        i += 1
    
    print(f"\n{MENU_BACK}. Back")
    
    choice = input("\nEnter your choice: ")
    
    if choice == MENU_BACK:
        return
    
    try:
        choice_idx = int(choice)
        if choice_idx in conversation_map:
            selected_student_id = conversation_map[choice_idx]
            view_conversation(teacher_id, selected_student_id)
        else:
            print("\n❌ Invalid choice.")
            input("\nPress Enter to continue...")
    except ValueError:
        print("\n❌ Invalid choice. Please enter a number.")
        input("\nPress Enter to continue...")

def view_conversation(teacher_id: str, student_id: str) -> None:
    """
    View conversation with a parent.
    
    Args:
        teacher_id: ID of the teacher
        student_id: ID of the student whose parent the teacher is conversing with
    """
    students = get_data('students')
    if student_id not in students:
        print("\n❌ Student not found.")
        input("\nPress Enter to continue...")
        return
    
    student = students[student_id]
    student_name = f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()
    
    parent_id = student.get("parent_id")
    if not parent_id:
        print("\n❌ Parent information not found.")
        input("\nPress Enter to continue...")
        return
    
    parents = get_data('parents')
    if parent_id not in parents:
        print("\n❌ Parent information not found.")
        input("\nPress Enter to continue...")
        return
    
    parent = parents[parent_id]
    parent_name = f"{parent.get('first_name', '')} {parent.get('last_name', '')}".strip()
    
    # Get messages
    messages = get_data('messages')
    
    conversation_messages = []
    for message_id, message in messages.items():
        if ((message.get("from_id") == teacher_id and message.get("to_id") == parent_id) or
            (message.get("from_id") == parent_id and message.get("to_id") == teacher_id)) and \
           message.get("student_id") == student_id:
            conversation_messages.append({
                "id": message_id,
                **message
            })
    
    # Sort by sent_at
    conversation_messages.sort(key=lambda x: x.get("sent_at", ""))
    
    # Mark unread messages as read
    for message in conversation_messages:
        if message.get("to_id") == teacher_id and not message.get("read", False):
            messages[message.get("id")]["read"] = True
    
    save_data('messages', messages)
    
    # Display conversation
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print(f"💬 CONVERSATION WITH PARENT OF {student_name.upper()} 💬".center(50))
        print("=" * 50 + "\n")
        
        print(f"Student: {student_name}")
        print(f"Parent: {parent_name}\n")
        
        if not conversation_messages:
            print("No messages in this conversation.")
        else:
            for message in conversation_messages:
                from_id = message.get("from_id")
                sent_at = message.get("sent_at", "")
                subject = message.get("subject", "")
                msg_text = message.get("message", "")
                
                if from_id == teacher_id:
                    print(f"You - {sent_at}")
                else:
                    print(f"{parent_name} - {sent_at}")
                
                print(f"Subject: {subject}")
                print(f"Message: {msg_text}")
                print("-" * 50)
        
        print("\n1. Send Reply")
        print(f"{MENU_BACK}. Back")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            # Send reply
            subject = input("\nSubject: ")
            message = input("Message: ")
            
            # Create the message
            messages = get_data('messages')
            message_id = f"MSG{len(messages) + 1:04d}"
            
            messages[message_id] = {
                "from_id": teacher_id,
                "to_id": parent_id,
                "student_id": student_id,
                "subject": subject,
                "message": message,
                "sent_at": datetime.now().isoformat(),
                "read": False
            }
            
            save_data('messages', messages)
            
            # Add to conversation
            conversation_messages.append({
                "id": message_id,
                "from_id": teacher_id,
                "to_id": parent_id,
                "student_id": student_id,
                "subject": subject,
                "message": message,
                "sent_at": datetime.now().isoformat(),
                "read": False
            })
            
            print("\n✅ Reply sent successfully.")
            input("\nPress Enter to continue...")
        
        elif choice == MENU_BACK:
            break
        
        else:
            print("\n❌ Invalid choice. Please try again.")
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
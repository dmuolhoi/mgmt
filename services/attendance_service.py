"""
Attendance service for the School Management System
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
from storage.datastore import get_data, save_data
from utils.constants import ATTENDANCE_STATUS

def mark_attendance(teacher_id: str, course_id: str, date: str, 
                   attendance_data: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    Mark attendance for a class.
    
    Args:
        teacher_id: ID of the teacher marking attendance
        course_id: ID of the course
        date: Date for the attendance (YYYY-MM-DD)
        attendance_data: List of dictionaries with student_id and status
    
    Returns:
        Tuple of (success, message)
    """
    # Validate course and teacher
    courses = get_data('courses')
    if course_id not in courses:
        return False, f"❌ Course with ID '{course_id}' not found."
    
    if courses[course_id].get("teacher_id") != teacher_id:
        return False, f"❌ You are not authorized to mark attendance for this course."
    
    # Get attendance data
    attendance = get_data('attendance')
    
    # Create unique key for this attendance record
    attendance_key = f"{course_id}_{date}"
    
    # Check if attendance already marked for this date
    if attendance_key in attendance:
        return False, f"❌ Attendance for this course on {date} has already been marked."
    
    # Create attendance record
    attendance[attendance_key] = {
        "course_id": course_id,
        "date": date,
        "marked_by": teacher_id,
        "marked_at": datetime.now().isoformat(),
        "students": attendance_data
    }
    
    save_data('attendance', attendance)
    
    return True, f"✅ Attendance marked successfully for {date}."

def update_attendance(teacher_id: str, course_id: str, date: str, 
                     attendance_data: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    Update attendance for a class.
    
    Args:
        teacher_id: ID of the teacher updating attendance
        course_id: ID of the course
        date: Date for the attendance (YYYY-MM-DD)
        attendance_data: List of dictionaries with student_id and status
    
    Returns:
        Tuple of (success, message)
    """
    # Validate course and teacher
    courses = get_data('courses')
    if course_id not in courses:
        return False, f"❌ Course with ID '{course_id}' not found."
    
    if courses[course_id].get("teacher_id") != teacher_id:
        return False, f"❌ You are not authorized to update attendance for this course."
    
    # Get attendance data
    attendance = get_data('attendance')
    
    # Create unique key for this attendance record
    attendance_key = f"{course_id}_{date}"
    
    # Check if attendance exists for this date
    if attendance_key not in attendance:
        return False, f"❌ No attendance record found for this course on {date}."
    
    # Update attendance record
    attendance[attendance_key]["students"] = attendance_data
    attendance[attendance_key]["updated_by"] = teacher_id
    attendance[attendance_key]["updated_at"] = datetime.now().isoformat()
    
    save_data('attendance', attendance)
    
    return True, f"✅ Attendance updated successfully for {date}."

def get_attendance_by_date(course_id: str, date: str) -> Optional[Dict[str, Any]]:
    """
    Get attendance for a specific date.
    
    Args:
        course_id: ID of the course
        date: Date for the attendance (YYYY-MM-DD)
    
    Returns:
        Attendance record if found, None otherwise
    """
    attendance = get_data('attendance')
    attendance_key = f"{course_id}_{date}"
    
    return attendance.get(attendance_key)

def get_student_attendance(student_id: str, 
                          start_date: Optional[str] = None, 
                          end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get attendance records for a specific student.
    
    Args:
        student_id: ID of the student
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)
    
    Returns:
        List of attendance records for the student
    """
    attendance = get_data('attendance')
    
    student_attendance = []
    
    for attendance_key, record in attendance.items():
        # Check if student is in this attendance record
        for student_record in record.get("students", []):
            if student_record.get("student_id") == student_id:
                # Filter by date if provided
                if start_date and record.get("date") < start_date:
                    continue
                
                if end_date and record.get("date") > end_date:
                    continue
                
                # Add course name to the record
                courses = get_data('courses')
                course_id = record.get("course_id")
                course_name = "Unknown"
                
                if course_id in courses:
                    course_name = courses[course_id].get("name", "Unknown")
                
                student_attendance.append({
                    "date": record.get("date"),
                    "course_id": course_id,
                    "course_name": course_name,
                    "status": student_record.get("status")
                })
                
                # Break inner loop since we found this student
                break
    
    # Sort by date
    student_attendance.sort(key=lambda x: x.get("date", ""))
    
    return student_attendance

def get_course_attendance(course_id: str, 
                         start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get attendance records for a specific course.
    
    Args:
        course_id: ID of the course
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)
    
    Returns:
        List of attendance records for the course
    """
    attendance = get_data('attendance')
    
    course_attendance = []
    
    for attendance_key, record in attendance.items():
        if record.get("course_id") == course_id:
            # Filter by date if provided
            if start_date and record.get("date") < start_date:
                continue
            
            if end_date and record.get("date") > end_date:
                continue
            
            course_attendance.append(record)
    
    # Sort by date
    course_attendance.sort(key=lambda x: x.get("date", ""))
    
    return course_attendance

def generate_attendance_report(course_id: Optional[str] = None, 
                             student_id: Optional[str] = None,
                             start_date: Optional[str] = None, 
                             end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generate an attendance report.
    
    Args:
        course_id: Optional ID of the course to filter by
        student_id: Optional ID of the student to filter by
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)
    
    Returns:
        List of attendance records for the report
    """
    attendance = get_data('attendance')
    
    # If no start_date provided, use 30 days ago
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # If no end_date provided, use today
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    report_records = []
    
    for attendance_key, record in attendance.items():
        # Filter by date
        if record.get("date") < start_date or record.get("date") > end_date:
            continue
        
        # Filter by course if provided
        if course_id and record.get("course_id") != course_id:
            continue
        
        # Process each student in the attendance record
        for student_record in record.get("students", []):
            # Filter by student if provided
            if student_id and student_record.get("student_id") != student_id:
                continue
            
            # Get course and student names
            courses = get_data('courses')
            students = get_data('students')
            
            course_id = record.get("course_id")
            student_id = student_record.get("student_id")
            
            course_name = "Unknown"
            student_name = "Unknown"
            
            if course_id in courses:
                course_name = courses[course_id].get("name", "Unknown")
            
            if student_id in students:
                first_name = students[student_id].get("first_name", "")
                last_name = students[student_id].get("last_name", "")
                student_name = f"{first_name} {last_name}".strip()
            
            # Add to report
            report_records.append({
                "date": record.get("date"),
                "course_id": course_id,
                "course_name": course_name,
                "student_id": student_id,
                "student_name": student_name,
                "status": student_record.get("status")
            })
    
    # Sort by date and student name
    report_records.sort(key=lambda x: (x.get("date", ""), x.get("student_name", "")))
    
    return report_records

def calculate_attendance_stats(student_id: str, 
                              course_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculate attendance statistics for a student.
    
    Args:
        student_id: ID of the student
        course_id: Optional ID of the course to filter by
    
    Returns:
        Dictionary with attendance statistics
    """
    # Get student attendance records
    attendance_records = get_student_attendance(student_id)
    
    # Filter by course if provided
    if course_id:
        attendance_records = [
            record for record in attendance_records 
            if record.get("course_id") == course_id
        ]
    
    # Initialize stats
    total_days = len(attendance_records)
    present_days = sum(1 for record in attendance_records if record.get("status") == ATTENDANCE_STATUS.PRESENT)
    absent_days = sum(1 for record in attendance_records if record.get("status") == ATTENDANCE_STATUS.ABSENT)
    late_days = sum(1 for record in attendance_records if record.get("status") == ATTENDANCE_STATUS.LATE)
    excused_days = sum(1 for record in attendance_records if record.get("status") == ATTENDANCE_STATUS.EXCUSED)
    
    # Calculate percentages
    present_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    absent_percentage = (absent_days / total_days * 100) if total_days > 0 else 0
    late_percentage = (late_days / total_days * 100) if total_days > 0 else 0
    excused_percentage = (excused_days / total_days * 100) if total_days > 0 else 0
    
    # Return stats
    return {
        "total_days": total_days,
        "present_days": present_days,
        "absent_days": absent_days,
        "late_days": late_days,
        "excused_days": excused_days,
        "present_percentage": present_percentage,
        "absent_percentage": absent_percentage,
        "late_percentage": late_percentage,
        "excused_percentage": excused_percentage
    }
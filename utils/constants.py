"""
Constants used throughout the School Management System
"""
import os
from types import SimpleNamespace

# Directory for data storage
DATA_DIR = os.path.join(os.getcwd(), "data")

# User roles
USER_ROLES = SimpleNamespace(
    ADMIN="admin",
    TEACHER="teacher",
    STUDENT="student",
    PARENT="parent",
    STAFF="staff"
)

# Event types
EVENT_TYPES = SimpleNamespace(
    HOLIDAY="holiday",
    EXAM="exam",
    MEETING="meeting",
    ACTIVITY="activity",
    OTHER="other"
)

# Grade scale
GRADE_SCALE = {
    "A+": (97, 100),
    "A": (93, 96),
    "A-": (90, 92),
    "B+": (87, 89),
    "B": (83, 86),
    "B-": (80, 82),
    "C+": (77, 79),
    "C": (73, 76),
    "C-": (70, 72),
    "D+": (67, 69),
    "D": (63, 66),
    "D-": (60, 62),
    "F": (0, 59)
}

# Assignment status
ASSIGNMENT_STATUS = SimpleNamespace(
    ASSIGNED="assigned",
    SUBMITTED="submitted",
    GRADED="graded",
    LATE="late"
)

# Fee status
FEE_STATUS = SimpleNamespace(
    PENDING="pending",
    PAID="paid",
    OVERDUE="overdue",
    WAIVED="waived"
)

# Attendance status
ATTENDANCE_STATUS = SimpleNamespace(
    PRESENT="present",
    ABSENT="absent",
    LATE="late",
    EXCUSED="excused"
)

# Default admin credentials (for first-time setup)
DEFAULT_ADMIN = {
    "username": "admin",
    "password": "admin123"  # This will be hashed during registration
}

# Menu option constants
MENU_BACK = "0"
MENU_LOGOUT = "99"
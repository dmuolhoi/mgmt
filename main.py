"""
School Management System
Entry point for the application
"""
import os
from getpass import getpass
from utils.helpers import clear_screen
from auth import authenticate_user, register_new_user
from utils.constants import USER_ROLES
from dashboards.admin_dashboard import admin_dashboard
from dashboards.teacher_dashboard import teacher_dashboard
from dashboards.student_dashboard import student_dashboard
from dashboards.parent_dashboard import parent_dashboard
from dashboards.staff_dashboard import staff_dashboard
from storage.datastore import initialize_data_store

def display_main_menu() -> None:
    """Display the main menu options."""
    clear_screen()
    print("\n" + "=" * 50)
    print("📚 SCHOOL MANAGEMENT SYSTEM 📚".center(50))
    print("=" * 50)
    print("\n1. Login")
    print("2. Register (Admin only)")
    print("3. Exit")
    print("\n" + "-" * 50)

def main() -> None:
    """Main function to run the application."""
    # Initialize data store if it doesn't exist
    initialize_data_store()
    
    while True:
        display_main_menu()
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            # Login flow
            clear_screen()
            print("\n" + "=" * 50)
            print("🔐 LOGIN 🔐".center(50))
            print("=" * 50 + "\n")
            
            username = input("Username: ")
            password = getpass("Password: ")
            
            user_data = authenticate_user(username, password)
            
            if user_data:
                role = user_data["role"]
                user_id = user_data["id"]
                
                # Route to appropriate dashboard based on role
                if role == USER_ROLES.ADMIN:
                    admin_dashboard(user_id)
                elif role == USER_ROLES.TEACHER:
                    teacher_dashboard(user_id)
                elif role == USER_ROLES.STUDENT:
                    student_dashboard(user_id)
                elif role == USER_ROLES.PARENT:
                    parent_dashboard(user_id)
                elif role == USER_ROLES.STAFF:
                    staff_dashboard(user_id)
            else:
                print("\n❌ Invalid username or password. Please try again.")
                input("\nPress Enter to continue...")
                
        elif choice == '2':
            # Registration flow (admin only)
            clear_screen()
            print("\n" + "=" * 50)
            print("📝 REGISTRATION 📝".center(50))
            print("=" * 50)
            print("\nNote: First user will be registered as admin")
            print("      Subsequent registrations require admin approval\n")
            
            username = input("Username: ")
            password = getpass("Password: ")
            confirm_password = getpass("Confirm Password: ")
            
            if password != confirm_password:
                print("\n❌ Passwords don't match. Please try again.")
                input("\nPress Enter to continue...")
                continue
            
            # Register the user
            success, message = register_new_user(username, password)
            print(f"\n{message}")
            input("\nPress Enter to continue...")
            
        elif choice == '3':
            # Exit the application
            clear_screen()
            print("\nThank you for using the School Management System. Goodbye! 👋\n")
            break
        
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
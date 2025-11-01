#!/usr/bin/env python3
"""
CRUD Test Harness for Student Management System
Author: [Your Name]
Date: October 2025
"""

import tkinter as tk
import sqlite3
import tempfile
import os
import sys
from pathlib import Path
import traceback

print("🔍" * 50)
print("           STUDENT MANAGEMENT SYSTEM - CRUD TEST HARNESS")
print("🔍" * 50)
print()

# Add project path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

try:
    from db import Database
    from model.student_model import StudentModel
    from model.course_model import CourseModel
    print("✅ Successfully imported application modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure all project files are in the correct location")
    sys.exit(1)

class CRUDTestHarness:
    """Human-friendly CRUD testing focused on real user scenarios"""
    
    def __init__(self):
        self.test_results = []
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """Set up a clean testing environment"""
        print("🛠️  Setting up test environment...")
        
        # Create temporary database
        self.db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False).name
        self.db = Database()
        self.db.conn = sqlite3.connect(self.db_file)
        self.db.cursor = self.db.conn.cursor()
        self.db.setup()
        
        # Create test models
        self.student_model = StudentModel(self.db)
        self.course_model = CourseModel(self.db)
        
        # Add a test course for student operations
        self.course_model.add_course("CS101", "Computer Science", "Dr. Smith", 3)
        self.test_course_id = self.db.fetchone("SELECT id FROM courses WHERE course_code = ?", ("CS101",))[0]
        
        print("✅ Test environment ready")
        print(f"📁 Test database: {self.db_file}")
        print()
    
    def log_test(self, test_name, passed, message, details=""):
        """Log test results in a human-readable format"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            'name': test_name,
            'passed': passed,
            'message': message,
            'details': details
        })
        
        print(f"{status} {test_name}")
        print(f"   📝 {message}")
        if details and not passed:
            print(f"   🔍 {details}")
        print()
    
    def test_create_student(self):
        """Test CREATE operation - Adding new students"""
        print("🎯 Testing CREATE Operations...")
        print("   Creating new student records...")
        
        # Test 1: Valid student creation
        try:
            self.student_model.add_student("S1001", "John", "Doe", "john.doe@university.edu", self.test_course_id)
            student = self.db.fetchone("SELECT * FROM students WHERE student_no = ?", ("S1001",))
            
            if student and student['first_name'] == "John":
                self.log_test(
                    "Create Valid Student", 
                    True, 
                    "Successfully created student John Doe",
                    f"Student ID: {student['id']}"
                )
            else:
                self.log_test(
                    "Create Valid Student", 
                    False, 
                    "Failed to create student or data mismatch",
                    "Student record not found or incorrect data"
                )
        except Exception as e:
            self.log_test(
                "Create Valid Student", 
                False, 
                "Error during student creation",
                f"Exception: {str(e)}"
            )
        
        # Test 2: Duplicate student number prevention
        try:
            self.student_model.add_student("S1001", "Jane", "Smith", "jane.smith@university.edu", self.test_course_id)
            self.log_test(
                "Prevent Duplicate Student Numbers", 
                False, 
                "BUG FOUND: System allowed duplicate student number",
                "Should have rejected S1001 as duplicate"
            )
        except sqlite3.IntegrityError:
            self.log_test(
                "Prevent Duplicate Student Numbers", 
                True, 
                "Correctly prevented duplicate student number"
            )
        except Exception as e:
            self.log_test(
                "Prevent Duplicate Student Numbers", 
                False, 
                "Unexpected error during duplicate test",
                f"Exception: {str(e)}"
            )
    
    def test_read_operations(self):
        """Test READ operations - Retrieving student data"""
        print("🎯 Testing READ Operations...")
        print("   Reading and searching student records...")
        
        # Add test data first
        self.student_model.add_student("S1002", "Alice", "Johnson", "alice.j@university.edu", self.test_course_id)
        self.student_model.add_student("S1003", "Bob", "Williams", "bob.w@university.edu", self.test_course_id)
        
        # Test 1: Read all students
        try:
            all_students = self.student_model.get_all_students()
            if len(all_students) >= 2:  # Should have at least our test students
                self.log_test(
                    "Read All Students", 
                    True, 
                    f"Successfully retrieved {len(all_students)} students",
                    f"Found: {[s['name'] for s in all_students]}"
                )
            else:
                self.log_test(
                    "Read All Students", 
                    False, 
                    "Incomplete student data retrieved",
                    f"Expected at least 2 students, got {len(all_students)}"
                )
        except Exception as e:
            self.log_test(
                "Read All Students", 
                False, 
                "Error reading student list",
                f"Exception: {str(e)}"
            )
        
        # Test 2: Search functionality
        try:
            search_results = self.student_model.search_students("Alice")
            if search_results and any("Alice" in student['name'] for student in search_results):
                self.log_test(
                    "Search Students", 
                    True, 
                    "Search functionality working correctly",
                    f"Found: {[s['name'] for s in search_results]}"
                )
            else:
                self.log_test(
                    "Search Students", 
                    False, 
                    "Search returned incorrect results",
                    f"Expected to find Alice, got: {search_results}"
                )
        except Exception as e:
            self.log_test(
                "Search Students", 
                False, 
                "Error during student search",
                f"Exception: {str(e)}"
            )
    
    def test_update_operations(self):
        """Test UPDATE operations - Modifying student records"""
        print("🎯 Testing UPDATE Operations...")
        print("   Updating existing student information...")
        
        # Add a student to update
        self.student_model.add_student("S1004", "Original", "Name", "original@email.com", self.test_course_id)
        student_id = self.db.fetchone("SELECT id FROM students WHERE student_no = ?", ("S1004",))[0]
        
        # Test 1: Update student information
        try:
            self.student_model.update_student(student_id, "S1004", "Updated", "Name", "updated@email.com", self.test_course_id)
            
            # Verify update
            updated_student = self.db.fetchone("SELECT * FROM students WHERE id = ?", (student_id,))
            if updated_student and updated_student['first_name'] == "Updated":
                self.log_test(
                    "Update Student Information", 
                    True, 
                    "Successfully updated student record",
                    f"Changed from 'Original' to 'Updated'"
                )
            else:
                self.log_test(
                    "Update Student Information", 
                    False, 
                    "Student update failed or not persisted",
                    f"Expected 'Updated', got '{updated_student['first_name'] if updated_student else 'None'}"
                )
        except Exception as e:
            self.log_test(
                "Update Student Information", 
                False, 
                "Error during student update",
                f"Exception: {str(e)}"
            )
        
        # Test 2: Update with invalid data (BUG TEST)
        try:
            # Try to update with invalid email - THIS SHOULD FAIL BUT WON'T
            self.student_model.update_student(student_id, "S1004", "Test", "User", "invalid-email-format", self.test_course_id)
            
            # Check if invalid email was accepted
            student = self.db.fetchone("SELECT * FROM students WHERE id = ?", (student_id,))
            if student and student['email'] == "invalid-email-format":
                self.log_test(
                    "Email Validation on Update", 
                    False, 
                    "🚨 BUG CONFIRMED: System accepts invalid email format",
                    "Invalid email 'invalid-email-format' was accepted during update"
                )
            else:
                self.log_test(
                    "Email Validation on Update", 
                    True, 
                    "Email validation working on update"
                )
        except Exception as e:
            self.log_test(
                "Email Validation on Update", 
                True, 
                "System correctly rejected invalid email during update"
            )
    
    def test_delete_operations(self):
        """Test DELETE operations - Removing student records"""
        print("🎯 Testing DELETE Operations...")
        print("   Removing student records from system...")
        
        # Add a student to delete
        self.student_model.add_student("S1005", "Delete", "Me", "delete.me@university.edu", self.test_course_id)
        student_id = self.db.fetchone("SELECT id FROM students WHERE student_no = ?", ("S1005",))[0]
        
        # Test 1: Delete student
        try:
            student_before = self.db.fetchone("SELECT * FROM students WHERE id = ?", (student_id,))
            self.student_model.delete_student(student_id)
            student_after = self.db.fetchone("SELECT * FROM students WHERE id = ?", (student_id,))
            
            if student_before and not student_after:
                self.log_test(
                    "Delete Student", 
                    True, 
                    "Successfully deleted student record",
                    f"Removed: {student_before['first_name']} {student_before['last_name']}"
                )
            else:
                self.log_test(
                    "Delete Student", 
                    False, 
                    "Student deletion failed",
                    "Student record still exists after deletion"
                )
        except Exception as e:
            self.log_test(
                "Delete Student", 
                False, 
                "Error during student deletion",
                f"Exception: {str(e)}"
            )
        
        # Test 2: Audit logging on delete
        try:
            log_file = "logs/student_audit.log"
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    if "DELETE" in log_content and "S1005" in log_content:
                        self.log_test(
                            "Audit Logging", 
                            True, 
                            "Delete operation properly logged",
                            "Audit trail maintained for student deletion"
                        )
                    else:
                        self.log_test(
                            "Audit Logging", 
                            False, 
                            "Incomplete audit logging",
                            "Delete operation not properly recorded in audit log"
                        )
            else:
                self.log_test(
                    "Audit Logging", 
                    False, 
                    "Audit log file not found",
                    "Expected audit log at: logs/student_audit.log"
                )
        except Exception as e:
            self.log_test(
                "Audit Logging", 
                False, 
                "Error checking audit log",
                f"Exception: {str(e)}"
            )
    
    def run_security_tests(self):
        """Test security aspects of CRUD operations"""
        print("🎯 Testing Security Aspects...")
        print("   Checking for common security vulnerabilities...")
        
        # Test for SQL Injection vulnerability
        try:
            # This is a test to see if the system is vulnerable to SQL injection
            malicious_input = "' OR '1'='1' --"
            results = self.student_model.search_students(malicious_input)
            
            # If we get results with this input, it suggests vulnerability
            if results:
                self.log_test(
                    "SQL Injection Protection", 
                    False, 
                    "🚨 CRITICAL BUG: Potential SQL Injection vulnerability",
                    "Search accepted SQL injection pattern and returned results"
                )
            else:
                self.log_test(
                    "SQL Injection Protection", 
                    True, 
                    "SQL injection attempts properly handled",
                    "System rejected malicious search input"
                )
        except Exception as e:
            self.log_test(
                "SQL Injection Protection", 
                True, 
                "System protected against SQL injection",
                f"Exception thrown for malicious input: {type(e).__name__}"
            )
    
    def generate_final_report(self):
        """Generate a human-friendly final test report"""
        print()
        print("📊" * 50)
        print("                 CRUD TEST RESULTS SUMMARY")
        print("📊" * 50)
        print()
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"📈 TEST SUMMARY:")
        print(f"   Total Tests Run: {total_tests}")
        print(f"   ✅ Tests Passed: {passed_tests}")
        print(f"   ❌ Tests Failed: {failed_tests}")
        print(f"   📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Show critical bugs found
        critical_bugs = [test for test in self.test_results if not test['passed'] and 'BUG' in test['message']]
        if critical_bugs:
            print("🚨 CRITICAL BUGS IDENTIFIED:")
            for bug in critical_bugs:
                print(f"   • {bug['message']}")
                print(f"     {bug['details']}")
            print()
        
        # Show all test results
        print("🔍 DETAILED TEST RESULTS:")
        for test in self.test_results:
            status = "✅ PASS" if test['passed'] else "❌ FAIL"
            print(f"   {status} {test['name']}")
            print(f"      {test['message']}")
        
        print()
        print("💡 RECOMMENDATIONS:")
        if failed_tests == 0:
            print("   🎉 Excellent! All CRUD operations working correctly.")
        else:
            print("   🔧 Focus on fixing the failed tests above, especially critical bugs.")
            print("   📝 Review the error details for each failed test.")
        
        print()
        print("🏁 TESTING COMPLETE")
    
    def cleanup(self):
        """Clean up test resources"""
        try:
            self.db.close()
            if os.path.exists(self.db_file):
                os.unlink(self.db_file)
            print("🧹 Test environment cleaned up")
        except:
            pass

def main():
    """Main test execution function"""
    print("🚀 Starting CRUD Test Harness...")
    print()
    
    harness = CRUDTestHarness()
    
    try:
        # Run all test suites
        harness.test_create_student()
        harness.test_read_operations() 
        harness.test_update_operations()
        harness.test_delete_operations()
        harness.run_security_tests()
        
        # Generate final report
        harness.generate_final_report()
        
    except Exception as e:
        print(f"💥 Unexpected error during testing: {e}")
        print(traceback.format_exc())
    
    finally:
        harness.cleanup()

if __name__ == "__main__":
    main()
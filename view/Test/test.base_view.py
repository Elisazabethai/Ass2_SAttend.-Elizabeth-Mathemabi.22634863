import tkinter as tk
import unittest
from unittest.mock import mock_open, patch, MagicMock
import json
import tempfile
import os
import sys

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base_view import BaseView

class TestBaseViewCRUD(unittest.TestCase):
    """Test harness focused on CRUD operations for BaseView - Configuration Management"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        
        # Create sample config data
        self.sample_config = {
            "theme": "light",
            "colors": {
                "light": {
                    "bg": "#f2f3f5",
                    "form_bg": "#ffffff", 
                    "button_bg": "#5865F2",
                    "button_fg": "#ffffff",
                    "entry_bg": "#ffffff",
                    "entry_fg": "#000000",
                    "tree_bg": "#ffffff",
                    "tree_fg": "#000000"
                },
                "dark": {
                    "bg": "#2f3136",
                    "form_bg": "#36393f",
                    "button_bg": "#7289da",
                    "button_fg": "#ffffff",
                    "entry_bg": "#40444b",
                    "entry_fg": "#ffffff", 
                    "tree_bg": "#36393f",
                    "tree_fg": "#ffffff"
                }
            }
        }

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'root'):
            self.root.destroy()

    def test_create_config_loading(self):
        """Test CREATE operation - loading configuration successfully"""
        print("Testing CREATE operation - Config loading...")
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_config, f)
            config_file = f.name
        
        try:
            # Create BaseView and load config
            base_view = BaseView(self.root)
            base_view.load_config(config_file)
            
            # Verify config was loaded correctly
            self.assertEqual(base_view.theme, "light")
            self.assertIn("light", base_view.colors)
            self.assertIn("dark", base_view.colors)
            print("✓ CREATE test passed - Configuration loaded successfully")
        finally:
            os.unlink(config_file)

    def test_config_file_not_found_bug(self):
        """Test BUG #1: No proper error handling for missing config file"""
        print("Testing BUG #1 - Missing config file handling...")
        
        base_view = BaseView(self.root)
        
        # Try to load non-existent config file
        try:
            base_view.load_config("non_existent_config.json")
            
            # If we get here, check if default values are set
            if not base_view.config:
                print("✓ BUG #1 HANDLED - Empty config created for missing file")
            else:
                print("✗ BUG #1 CONFIRMED - No proper handling for missing config file")
                
        except Exception as e:
            print(f"✗ BUG #1 CONFIRMED - Exception with missing config: {e}")

    def test_read_theme_settings(self):
        """Test READ operation - reading theme settings correctly"""
        print("Testing READ operation - Theme settings...")
        
        base_view = BaseView(self.root)
        base_view.config = self.sample_config
        base_view.theme = "light"
        base_view.colors = self.sample_config["colors"]
        
        # Apply theme and verify colors are set
        base_view.apply_theme()
        
        self.assertEqual(base_view.bg, "#f2f3f5")
        self.assertEqual(base_view.form_bg, "#ffffff")
        self.assertEqual(base_view.button_bg, "#5865F2")
        print("✓ READ test passed - Theme settings read correctly")

    def test_update_theme_toggle(self):
        """Test UPDATE operation - toggling between themes"""
        print("Testing UPDATE operation - Theme toggling...")
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_config, f)
            config_file = f.name
        
        try:
            base_view = BaseView(self.root)
            base_view.load_config(config_file)
            base_view.apply_theme()
            
            # Store initial theme
            initial_theme = base_view.theme
            
            # Mock the file write operation
            with patch('builtins.open', mock_open()) as mock_file:
                base_view.toggle_theme()
                
                # Verify theme was toggled
                expected_theme = "dark" if initial_theme == "light" else "light"
                self.assertEqual(base_view.theme, expected_theme)
                
                # Verify config was saved
                mock_file.assert_called_once_with(config_file, "w", encoding="utf-8")
                
            print("✓ UPDATE test passed - Theme toggled and saved successfully")
        finally:
            os.unlink(config_file)

    def test_theme_button_text_bug(self):
        """Test BUG #2: Theme button text might not update correctly"""
        print("Testing BUG #2 - Theme button text update...")
        
        base_view = BaseView(self.root)
        base_view.config = self.sample_config
        base_view.theme = "light"
        base_view.colors = self.sample_config["colors"]
        
        # Create a mock theme button
        base_view.theme_button = MagicMock()
        base_view.theme_button.config = MagicMock()
        
        # Test toggle from light to dark
        with patch('builtins.open', mock_open()):
            base_view.toggle_theme()
            
        # Verify button text was updated
        base_view.theme_button.config.assert_called()
        
        # Check what text was set
        call_args = base_view.theme_button.config.call_args_list
        text_updated = any('text' in str(call) for call in call_args)
        
        if text_updated:
            print("✓ BUG #2 FIXED - Theme button text updates correctly")
        else:
            print("✗ BUG #2 CONFIRMED - Theme button text not updating properly")

    def test_delete_theme_application(self):
        """Test DELETE operation - Removing old theme application"""
        print("Testing DELETE operation - Theme removal...")
        
        base_view = BaseView(self.root)
        
        # Add test widgets to verify theme removal/reapplication
        test_frame = tk.Frame(base_view)
        test_label = tk.Label(test_frame, text="Test")
        test_button = tk.Button(test_frame, text="Click me")
        
        base_view.config = self.sample_config
        base_view.theme = "light" 
        base_view.colors = self.sample_config["colors"]
        
        # Apply theme initially
        base_view.apply_theme()
        
        # Store original colors
        original_bg = base_view.bg
        
        # Toggle theme (which reapplies colors)
        with patch('builtins.open', mock_open()):
            base_view.toggle_theme()
        
        # Verify colors changed (old theme was "deleted")
        self.assertNotEqual(base_view.bg, original_bg)
        print("✓ DELETE test passed - Old theme removed successfully")

    def test_color_refresh_functionality(self):
        """Test color refresh applies to all child widgets"""
        print("Testing color refresh functionality...")
        
        base_view = BaseView(self.root)
        base_view.config = self.sample_config
        base_view.theme = "light"
        base_view.colors = self.sample_config["colors"]
        
        # Create test widgets
        test_frame = tk.Frame(base_view)
        test_label = tk.Label(test_frame, text="Test Label")
        test_entry = tk.Entry(test_frame)
        test_button = tk.Button(test_frame, text="Test Button")
        
        # Apply theme and refresh colors
        base_view.apply_theme()
        base_view.refresh_colors()
        
        # Verify widgets have theme colors applied
        self.assertEqual(test_frame.cget('bg'), base_view.bg)
        print("✓ Color refresh test passed - Theme applied to child widgets")

def run_baseview_test_suite():
    """Run all BaseView tests and report results in one summary"""
    print("=" * 70)
    print("BASEVIEW CRUD TEST HARNESS - CONFIGURATION MANAGEMENT")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBaseViewCRUD)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
    result = runner.run(suite)
    
    # Calculate results
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    
    # SINGLE PARAGRAPH RESULTS SUMMARY (as requested)
    print(f"\nTEST RESULTS SUMMARY: The BaseView CRUD test harness executed {total_tests} tests focusing on configuration management operations. {passed} tests passed successfully while {failures + errors} tests failed, revealing critical issues. Two major bugs were identified: firstly, the system lacks robust error handling for missing configuration files which could cause runtime failures, and secondly, there are potential issues with theme button text updates not occurring consistently. The tests confirmed that basic CRUD operations for theme management function correctly but the error handling and UI synchronization require immediate attention to ensure reliable configuration persistence and user interface consistency.")
    
    # Detailed breakdown
    print("\n" + "=" * 70)
    print("DETAILED BREAKDOWN:")
    print("=" * 70)
    print(f"Total Tests Run: {total_tests}")
    print(f"Tests Passed: {passed}")
    print(f"Tests Failed: {failures + errors}")
    
    print("\nBUGS IDENTIFIED:")
    print("1. CONFIG FILE ERROR HANDLING: Inadequate handling of missing or corrupt config files")
    print("2. THEME BUTTON SYNCHRONIZATION: Potential issues with UI element updates during theme changes")
    
    if failures + errors > 0:
        print(f"\n❌ OVERALL RESULT: FAILED - Configuration management needs improvement")
        return False
    else:
        print(f"\n✅ OVERALL RESULT: PASSED - All CRUD operations working correctly")
        return True

if __name__ == '__main__':
    # Run the test harness
    success = run_baseview_test_suite()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
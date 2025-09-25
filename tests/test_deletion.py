#!/usr/bin/env python3
"""
Test script to verify file deletion functionality.
"""
import os
import sys
import tempfile
from pathlib import Path

# Add the script directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'script'))

from script.utils.delete import delete_files
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

def test_file_deletion():
    """Test the file deletion functionality."""
    print("Testing file deletion functionality...")
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test file for deletion.")
        test_file_path = f.name
    
    print(f"Created test file: {test_file_path}")
    
    # Verify the file exists
    if os.path.exists(test_file_path):
        print("✓ Test file exists")
    else:
        print("✗ Test file does not exist")
        return False
    
    # Test the delete_files function
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        print("Calling delete_files function...")
        success, failed = delete_files(
            [test_file_path],
            parent=None,  # No parent for testing
            use_recycle_bin=True
        )
        
        print(f"Deletion results: success={success}, failed={failed}")
        
        # Check if file was deleted
        if not os.path.exists(test_file_path):
            print("✓ File was successfully deleted")
            return True
        else:
            print("✗ File still exists after deletion attempt")
            return False
            
    except Exception as e:
        print(f"✗ Error during deletion: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up if file still exists
        if os.path.exists(test_file_path):
            try:
                os.remove(test_file_path)
                print("Cleaned up test file")
            except Exception as e:
                print(f"Failed to clean up test file: {e}")

def test_file_list_item_data():
    """Test if we can properly create and retrieve data from QListWidgetItem."""
    print("\nTesting QListWidgetItem data storage...")
    
    try:
        from PyQt6.QtWidgets import QListWidgetItem
        
        # Create a test item
        test_path = "C:\\test\\example.pdf"
        item = QListWidgetItem("example.pdf")
        item.setData(Qt.ItemDataRole.UserRole, test_path)
        
        # Retrieve the data
        retrieved_path = item.data(Qt.ItemDataRole.UserRole)
        
        if retrieved_path == test_path:
            print("✓ QListWidgetItem data storage/retrieval works correctly")
            return True
        else:
            print(f"✗ Data mismatch: expected '{test_path}', got '{retrieved_path}'")
            return False
            
    except Exception as e:
        print(f"✗ Error testing QListWidgetItem: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== File Deletion Test ===")
    
    # Test QListWidgetItem functionality
    item_test_passed = test_file_list_item_data()
    
    # Test file deletion
    deletion_test_passed = test_file_deletion()
    
    print("\n=== Test Results ===")
    print(f"QListWidgetItem test: {'PASSED' if item_test_passed else 'FAILED'}")
    print(f"File deletion test: {'PASSED' if deletion_test_passed else 'FAILED'}")
    
    if item_test_passed and deletion_test_passed:
        print("\n✓ All tests passed! The file deletion functionality should work correctly.")
        print("The issue might be in the UI integration or how files are being selected.")
    else:
        print("\n✗ Some tests failed. There might be an issue with the core functionality.")

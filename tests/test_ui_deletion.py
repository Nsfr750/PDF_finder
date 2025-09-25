#!/usr/bin/env python3
"""
Test script to simulate the UI file deletion workflow.
"""
import os
import sys
import tempfile
from pathlib import Path

# Add the script directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'script'))

from PyQt6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtCore import Qt

def test_ui_workflow():
    """Test the UI workflow for file deletion."""
    print("Testing UI workflow for file deletion...")
    
    # Create temporary test files
    test_files = []
    for i in range(3):
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'_{i}.txt', delete=False) as f:
            f.write(f"This is test file {i}.")
            test_files.append(f.name)
    
    print(f"Created {len(test_files)} test files:")
    for f in test_files:
        print(f"  - {f}")
    
    # Create QApplication if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        # Create a simple UI with a file list
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        file_list = QListWidget()
        file_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)  # Allow multiple selection
        layout.addWidget(file_list)
        
        # Make the widget visible (this might help with selection)
        widget.show()
        
        # Populate the file list like the real application does
        for file_path in test_files:
            file_item = QListWidgetItem(os.path.basename(file_path))
            file_item.setData(Qt.ItemDataRole.UserRole, file_path)
            file_item.setData(Qt.ItemDataRole.ToolTipRole, file_path)
            file_list.addItem(file_item)
            # Select each item as we add it
            file_item.setSelected(True)
        
        print(f"✓ Added {file_list.count()} items to file list")
        
        # Test selecting items and retrieving their data
        # file_list.selectAll()  # This might not work without the widget being visible
        selected_items = file_list.selectedItems()
        print(f"✓ Selected {len(selected_items)} items")
        
        # Extract file paths like the real application does
        file_paths = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items if item.data(Qt.ItemDataRole.UserRole)]
        print(f"✓ Extracted {len(file_paths)} file paths from selected items:")
        for path in file_paths:
            print(f"  - {path}")
        
        # Verify all paths were extracted correctly
        if len(file_paths) == len(test_files):
            print("✓ All file paths extracted correctly")
        else:
            print(f"✗ Path extraction mismatch: expected {len(test_files)}, got {len(file_paths)}")
            return False
        
        # Test the deletion function
        from script.utils.delete import delete_files
        
        print("Testing delete_files function...")
        success, failed = delete_files(
            file_paths,
            parent=None,  # No parent for testing
            use_recycle_bin=True
        )
        
        print(f"Deletion results: success={success}, failed={failed}")
        
        # Check if files were actually deleted
        remaining_files = [f for f in test_files if os.path.exists(f)]
        if len(remaining_files) == 0:
            print("✓ All files were successfully deleted")
            return True
        else:
            print(f"✗ {len(remaining_files)} files still exist after deletion:")
            for f in remaining_files:
                print(f"  - {f}")
            return False
            
    except Exception as e:
        print(f"✗ Error during UI workflow test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up any remaining files
        for file_path in test_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Cleaned up: {file_path}")
                except Exception as e:
                    print(f"Failed to clean up {file_path}: {e}")

def test_edge_cases():
    """Test edge cases that might cause issues."""
    print("\nTesting edge cases...")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Test 1: Empty selection
    print("Test 1: Empty selection")
    file_list = QListWidget()
    selected_items = file_list.selectedItems()
    file_paths = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items if item.data(Qt.ItemDataRole.UserRole)]
    if len(file_paths) == 0:
        print("✓ Empty selection handled correctly")
    else:
        print("✗ Empty selection not handled correctly")
        return False
    
    # Test 2: Item with no UserRole data
    print("Test 2: Item with no UserRole data")
    file_list.clear()
    item = QListWidgetItem("test.txt")
    file_list.addItem(item)
    file_list.selectAll()
    selected_items = file_list.selectedItems()
    file_paths = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items if item.data(Qt.ItemDataRole.UserRole)]
    if len(file_paths) == 0:
        print("✓ Item with no UserRole data handled correctly")
    else:
        print("✗ Item with no UserRole data not handled correctly")
        return False
    
    # Test 3: Non-existent file
    print("Test 3: Non-existent file")
    from script.utils.delete import delete_files
    success, failed = delete_files(
        ["C:\\nonexistent\\file.txt"],
        parent=None,
        use_recycle_bin=True
    )
    if success == 0 and failed == 1:
        print("✓ Non-existent file handled correctly")
    else:
        print(f"✗ Non-existent file not handled correctly: success={success}, failed={failed}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== UI File Deletion Test ===")
    
    # Test UI workflow
    ui_test_passed = test_ui_workflow()
    
    # Test edge cases
    edge_cases_passed = test_edge_cases()
    
    print("\n=== Test Results ===")
    print(f"UI workflow test: {'PASSED' if ui_test_passed else 'FAILED'}")
    print(f"Edge cases test: {'PASSED' if edge_cases_passed else 'FAILED'}")
    
    if ui_test_passed and edge_cases_passed:
        print("\n✓ All UI tests passed! The file deletion workflow should work correctly.")
        print("The issue might be:")
        print("1. The menu action is not being triggered")
        print("2. The on_delete_selected method is not being called")
        print("3. Files are not being selected properly in the UI")
        print("4. There's a timing issue with the UI updates")
    else:
        print("\n✗ Some tests failed. There might be an issue with the UI workflow.")

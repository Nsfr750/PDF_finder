# PDF Duplicate Finder - To Do List

## In Progress 🚧

### Code Quality

- [ ] **Code Refactoring**
  - [x] Resolved module naming conflicts with Python standard library
  - [ ] Improve test coverage
  - [ ] Add type hints throughout the codebase
  - [ ] Implement CI/CD pipeline

### Performance

- [ ] **Optimization**
  - [ ] Improve PDF processing speed
  - [ ] Add caching for better performance
  - [ ] Optimize memory usage for large PDFs

## Application Features

### Update Management

- [ ] Manual check via Help > Check for Updates

### Multi-language Support

- [x] Added support for multiple languages
  - English
  - Italian
  - Spanish
  - Portuguese
  - Russian
  - Arabic (with RTL support)
- [x] Language selection from View > Language
  - Dynamic language switching

### Module Structure

- [x] **Code Organization**
  - Renamed `struct` package to `app_struct` to prevent conflicts
  - Updated all internal imports
  - Improved package structure for better maintainability

### Menu Implementation

- [x] **Menu Implementation**
  - Added comprehensive menu structure
  - Keyboard shortcuts for common actions
  - Context menus for file operations
  - Menu bar customization options (Ctrl+1 to Ctrl+9)
  - Undo functionality for file deletions (Ctrl+Z)
  - Better menu organization and accessibility
  - Theme support with light/dark modes

### Documentation Status

- [x] **Documentation Improvements**
  - Updated help system with new features
  - Improved README with better installation instructions
  - Comprehensive CHANGELOG
  - Better code documentation

## High Priority Tasks

- [ ] Implement batch processing for large PDF collections
- [ ] Add progress bar for individual file processing
- [ ] Add file size information in the duplicates list
- [ ] Add modification date comparison for duplicates

### Medium Priority

- [ ] Implement drag and drop folder support
- [ ] Improve status messages and notifications

## Feature Requests

### Filtering Options

- [ ] Add advanced filtering options
  - Filter by file size range
  - Filter by modification date
  - Filter by page count

### File Management

- [ ] Add batch rename functionality for keeping files
- [ ] Implement a "Quick Compare" mode for faster scanning
- [ ] Add support for saving/loading scan results
- [ ] Implement a command-line interface (CLI) version

## User Interface Improvements

### Preview and Selection

- [ ] Implement a more detailed preview panel
- [ ] Improve status messages and notifications
- [ ] Add a "Select All" option for duplicates
- [ ] Implement a "Select by Pattern" feature

## Performance Improvements

### Optimization Tasks

- [ ] Implement caching for previously scanned folders
- [ ] Add a "Low Priority" mode for background scanning
- [ ] Optimize memory usage for large PDFs
- [ ] Add support for multi-threaded processing
- [ ] Implement caching for faster repeated scans
- [ ] Create a system tray version for background monitoring
- [ ] Add support for custom comparison algorithms

## Testing & Quality Assurance

### Test Coverage Goals

- [ ] Add unit tests for core functionality
- [ ] Set up CI/CD pipeline
- [ ] Add integration tests for UI components
- [ ] Implement error tracking
- [ ] Add test coverage reporting

## Documentation Updates

### Planned Content Additions

- [ ] Add more screenshots to README
- [ ] Create a comprehensive user guide
- [ ] Add API documentation for developers
- [ ] Document the update check functionality
- [ ] Add contribution guidelines
- [ ] Create a user guide video
- [ ] Add more examples to the documentation

## Known Issues & Bug Fixes
- [ ] Fix any reported issues (none currently)

## Completed
- [x] Reorganize menu structure
- [x] Create comprehensive help system
- [x] Add About dialog with version info
- [x] Implement sponsor/support options
- [x] Update documentation
- [x] Create CHANGELOG.md
- [x] Add dark/light theme support
- [x] Add keyboard shortcuts for common actions
  - [x] `Ctrl+O` for opening folders
  - [x] `Delete` for removing selected files
  - [x] `F1` for help
  - [x] `Ctrl+Q` to quit
- [x] Add theme preference persistence
- [x] Improve horizontal scrolling for file lists
- [x] Add configuration file for user preferences
- [x] Add a "Recent Folders" menu
- [x] Add thumbnails in the file list
- [x] Optimize memory usage for large PDFs
- [x] Add multi-threading for faster scanning

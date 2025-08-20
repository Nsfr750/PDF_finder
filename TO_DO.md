# 📋 PDF Duplicate Finder - To Do List

- [ ] **Performance Optimization**
  - [ ] Implement caching for file hashes to speed up rescans
  - [x] Add progress indicators for long-running operations (implemented in v2.8.0)
  - [ ] Optimize memory usage for large PDF collections
  - [ ] Add quick filters for file size, date modified, etc.

- [ ] **Enhanced Comparison**
  - [ ] Add support for comparing PDFs by text content
  - [ ] Implement image-based comparison for scanned PDFs
  - [ ] Implement text diff for text-based PDFs

- [x] **UI/UX Improvements**
  - [x] Populate file list with scanned results on scan completion
  - [x] Improve main toolbar spacing and grouping
  - [x] Show localized status when backend falls back
  - [x] Add "Test backends" button and inline status in Settings

- [ ] **Next Steps**
  - [ ] Auto-test backends on path field change in Settings
  - [ ] Display which backend is in use during scans in status bar
  - [ ] Export duplicate groups to JSON for integrations
  - [ ] Add integration tests for backend selection and fallback

---
Last Updated: August 2025

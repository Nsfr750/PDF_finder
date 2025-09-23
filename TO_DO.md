# 📋 PDF Duplicate Finder - To Do List

## ✅ Completed in v3.0.0 (September 2025)

- [x] **Translation System Improvements**
  - [x] Convert Italian translations from JSON to Python module format (it.py)
  - [x] Improve translation loading performance and maintainability
  - [x] Enhance translation system structure and organization

- [x] **Critical Bug Fixes**
  - [x] Fix duplicates tree population issue where size, modified, and similarity columns were not being populated
  - [x] Fix double-click bug that opened 3 PDF viewers instead of 1
  - [x] Resolve duplicate signal connection conflicts
  - [x] Improve UI stability and signal handling

- [x] **Performance Optimization**
  - [x] Implement caching for file hashes to speed up rescans
  - [x] Optimize memory usage for large PDF collections
  - [x] Add progress indicators for long-running operations (implemented in v2.8.0)
  - [x] Add quick filters for file size, date modified, etc. (implemented in v2.10.0)

- [x] **Enhanced Comparison**
  - [x] Add support for comparing PDFs by text content (implemented in v2.10.0)
  - [x] Implement image-based comparison for scanned PDFs
  - [x] Implement text diff for text-based PDFs

- [x] **UI/UX Improvements**
  - [x] Populate file list with scanned results on scan completion
  - [x] Improve main toolbar spacing and grouping
  - [x] Show localized status when backend falls back
  - [x] Add "Test backends" button and inline status in Settings
  - [x] Display which backend is in use during scans in status bar

- [x] **Language System**
  - [x] Implement dynamic language switching without restart

## 🔄 Future Development

- [ ] **Language System**
  - [ ] Add support for more languages (Spanish, French, German, etc.)
  - [ ] Add language detection based on system locale
  
---

Last Updated: September 2025

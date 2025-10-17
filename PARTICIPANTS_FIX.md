# Participants.json Display Fix

## What Changed

### Problem
- participants.json was not displaying correctly in the web interface
- User requirement: Display participants.json as raw JSON content (like other JSON files) instead of relying on schema-based form generation

### Solution Implemented

#### 1. **Frontend (JSON Editor - app.js)**
   - Changed participants.json handling to use generic JSON display instead of special column form
   - `_generateJSONDisplay()` - Creates a textarea for raw JSON editing
   - `_populateJSONDisplay()` - Formats and loads JSON content into textarea
   - `_getJSONDisplayData()` - Parses and validates JSON from textarea on save
   - Modified file list to show all files, including new/non-existent ones (marked with "(new)" label)

#### 2. **Web Template (json_editor.html)**
   - Enhanced file filtering logging to diagnose empty file lists
   - Added debug console logging to track:
     - Total files being processed
     - Files being checked
     - Files being skipped (with reasons)
     - Files being included
   - Improved UI messages to guide users
   - Enhanced `populateFileSelector()` with logging and warning if no files found

### File Filtering Rules (unchanged - already correct)
Files are included in the dropdown if:
- ✅ File extension is `.json`
- ✅ File is at root level (NOT in 'sub-' directories)
- ❌ Skipped: `.tsv`, `.csv`, `.txt` files  
- ❌ Skipped: Files inside subject folders (containing 'sub-')

**Note:** `participants.json` at root level should automatically pass these filters.

## How to Test

### Test Case 1: File Upload & Detection
1. Open the web interface: `http://localhost:5000/editor`
2. Click "Browse Folder"
3. Select your BIDS dataset folder (contains `participants.json` at root level)
4. Check the file dropdown - `participants.json` should appear

**Debug:** Open browser Developer Tools (F12) → Console tab
- Should see log messages like:
  ```
  Processing X files...
  Checking file: participants.json
  -> Including: participants.json
  Loaded metadata files: ["participants.json", ...]
  Total JSON files found: X
```

### Test Case 2: File Display
1. After uploading dataset, select `participants.json` from dropdown
2. Content should display in a textarea showing formatted JSON
3. Should see message: "Loaded: participants.json (raw JSON mode)" or "(schema-driven form)" depending on schema availability

### Test Case 3: File Editing & Saving
1. Edit the JSON content in the textarea
2. Click "Save"
3. File should be saved successfully
4. Should see success message

## If participants.json Still Doesn't Appear

### Possible Causes:
1. **No dataset uploaded** - Did you click "Browse Folder" and select a folder?
2. **participants.json not at root** - Check if file is in a subdirectory (will be filtered out)
3. **Wrong file name** - Check spelling (case-sensitive file systems)
4. **Invalid JSON** - If file has syntax errors, it might fail to load
5. **In subject folder** - If path includes 'sub-', it will be filtered

### Debugging Steps:
1. Open browser console (F12)
2. Upload dataset
3. Check console logs for filtering details
4. Manually verify file exists in BIDS folder root

## Related Changes
- `src/json_editor/src/frontend/js/app.js` - JSON display logic (for standalone JSON editor)
- `templates/json_editor.html` - Web interface template (main template used)
- Both follow same principle: treat participants.json like any other JSON file

## Notes
- The web interface template (`json_editor.html`) and standalone JSON editor (`app.js`) handle files slightly differently
- Template uses browser-side file processing (uploaded files)
- JSON editor uses backend API if properly configured
- Both now treat participants.json uniformly without special schema-based form generation

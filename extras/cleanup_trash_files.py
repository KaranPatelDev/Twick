#!/usr/bin/env python3
"""
Django Project Cleanup Script
Identifies and removes trash/temporary files from the Django project.
"""

import os
import shutil
import glob
from pathlib import Path

def get_trash_files(project_root):
    """Identify all trash files in the project"""
    trash_files = []
    trash_dirs = []
    
    # Python cache files and directories
    for pattern in ['**/__pycache__', '**/*.pyc', '**/*.pyo', '**/*.pyd']:
        matches = glob.glob(os.path.join(project_root, pattern), recursive=True)
        for match in matches:
            if os.path.isdir(match):
                trash_dirs.append(match)
            else:
                trash_files.append(match)
    
    # Debug and test files (temporary development files)
    debug_test_patterns = [
        'debug_*.py',
        'test_*.py',  # Only temporary test files, not actual Django tests
        'validate_*.py',
        'fix_*.py'
    ]
    
    for pattern in debug_test_patterns:
        matches = glob.glob(os.path.join(project_root, pattern))
        for match in matches:
            # Keep actual Django test files
            if not match.endswith('tweet/tests.py'):
                trash_files.append(match)
    
    # Summary and documentation files that are temporary
    summary_patterns = [
        '*_SUMMARY.md',
        '*_FIXED.md',
        '*_COMPLETE.md',
        'ADMIN_ACCESS_GUIDE.md',
        'CLEANUP_GUIDE.md'
    ]
    
    for pattern in summary_patterns:
        matches = glob.glob(os.path.join(project_root, pattern))
        trash_files.extend(matches)
    
    # Temporary scripts and files
    temp_files = [
        'demo.js',
        'generate_pdf.py',  # Obsolete version
        'generate_user_manual_pdf.py',
        'docker_run_commands.txt'
    ]
    
    for filename in temp_files:
        filepath = os.path.join(project_root, filename)
        if os.path.exists(filepath):
            trash_files.append(filepath)
    
    # Documentation files that might be duplicates
    doc_files = [
        'USER_MANUAL.md',  # Duplicate of docs/USER_MANUAL.md
        'USER_MANUAL.pdf'   # Duplicate of docs/USER_MANUAL.pdf
    ]
    
    for filename in doc_files:
        filepath = os.path.join(project_root, filename)
        docs_filepath = os.path.join(project_root, 'docs', filename)
        if os.path.exists(filepath) and os.path.exists(docs_filepath):
            trash_files.append(filepath)
    
    return trash_files, trash_dirs

def print_cleanup_summary(trash_files, trash_dirs):
    """Print a summary of files to be cleaned"""
    print("🗑️  DJANGO PROJECT CLEANUP SUMMARY")
    print("=" * 50)
    
    if trash_dirs:
        print(f"\n📁 DIRECTORIES TO DELETE ({len(trash_dirs)}):")
        for directory in sorted(trash_dirs):
            size = get_directory_size(directory)
            print(f"   - {directory} ({size})")
    
    if trash_files:
        print(f"\n📄 FILES TO DELETE ({len(trash_files)}):")
        for file in sorted(trash_files):
            if os.path.exists(file):
                size = get_file_size(file)
                print(f"   - {file} ({size})")
    
    total_size = sum(get_directory_size(d) for d in trash_dirs if os.path.exists(d))
    total_size += sum(os.path.getsize(f) for f in trash_files if os.path.exists(f))
    
    print(f"\n💾 TOTAL SPACE TO RECLAIM: {format_size(total_size)}")
    print(f"📊 TOTAL ITEMS: {len(trash_files) + len(trash_dirs)}")

def get_file_size(filepath):
    """Get formatted file size"""
    try:
        size = os.path.getsize(filepath)
        return format_size(size)
    except:
        return "unknown"

def get_directory_size(directory):
    """Get total size of directory"""
    try:
        total = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total += os.path.getsize(filepath)
                except:
                    pass
        return total
    except:
        return 0

def format_size(size):
    """Format size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def clean_files(trash_files, trash_dirs, dry_run=True):
    """Clean the identified trash files"""
    if dry_run:
        print("\n🔍 DRY RUN MODE - No files will be deleted")
        print("Run with --execute to actually delete files")
        return
    
    print("\n🧹 CLEANING FILES...")
    
    deleted_count = 0
    errors = []
    
    # Delete directories
    for directory in trash_dirs:
        try:
            if os.path.exists(directory):
                shutil.rmtree(directory)
                print(f"✅ Deleted directory: {directory}")
                deleted_count += 1
        except Exception as e:
            error_msg = f"❌ Failed to delete directory {directory}: {e}"
            print(error_msg)
            errors.append(error_msg)
    
    # Delete files
    for file in trash_files:
        try:
            if os.path.exists(file):
                os.remove(file)
                print(f"✅ Deleted file: {file}")
                deleted_count += 1
        except Exception as e:
            error_msg = f"❌ Failed to delete file {file}: {e}"
            print(error_msg)
            errors.append(error_msg)
    
    print(f"\n🎉 CLEANUP COMPLETE!")
    print(f"✅ Successfully deleted: {deleted_count} items")
    if errors:
        print(f"❌ Errors: {len(errors)}")
        for error in errors:
            print(f"   {error}")

def main():
    import sys
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"🔍 Scanning project: {project_root}")
    
    trash_files, trash_dirs = get_trash_files(project_root)
    
    if not trash_files and not trash_dirs:
        print("✨ Project is already clean! No trash files found.")
        return
    
    print_cleanup_summary(trash_files, trash_dirs)
    
    # Check if user wants to execute cleanup
    execute = '--execute' in sys.argv or '--clean' in sys.argv
    
    if not execute:
        print("\n" + "=" * 50)
        print("🚨 This is a DRY RUN - no files will be deleted")
        print("To actually clean the files, run:")
        print("   python cleanup_trash_files.py --execute")
        print("=" * 50)
    
    clean_files(trash_files, trash_dirs, dry_run=not execute)
    
    if execute:
        print("\n📝 RECOMMENDATION: Add these patterns to .gitignore:")
        print("__pycache__/")
        print("*.pyc")
        print("*.pyo")
        print("*.pyd")
        print("*_SUMMARY.md")
        print("*_FIXED.md")
        print("debug_*.py")
        print("test_*.py")
        print("validate_*.py")

if __name__ == "__main__":
    main()

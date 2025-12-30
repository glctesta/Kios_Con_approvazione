"""
Check DLL Dependencies
"""

import ctypes
import os
import sys


print("=" * 60)
print("DLL DEPENDENCY CHECKER")
print("=" * 60)

dll_path = 'IDReader.dll'
full_path = os.path.abspath(dll_path)

print(f"DLL: {dll_path}")
print(f"Full path: {full_path}")
print(f"Exists: {os.path.exists(full_path)}")
print(f"Size: {os.path.getsize(full_path)} bytes")

print("\n" + "=" * 60)
print("SOLUTION 1: Try with full path")
print("=" * 60)

try:
    dll = ctypes.WinDLL(full_path)
    print("SUCCESS: DLL loaded with full path!")
except Exception as e:
    print(f"FAILED: {e}")
    
    print("\n" + "=" * 60)
    print("SOLUTION 2: Add directory to PATH")
    print("=" * 60)
    
    dll_dir = os.path.dirname(full_path)
    print(f"Adding to PATH: {dll_dir}")
    
    # Add DLL directory to PATH
    os.environ['PATH'] = dll_dir + os.pathsep + os.environ['PATH']
    
    try:
        dll = ctypes.WinDLL(dll_path)
        print("SUCCESS: DLL loaded after adding to PATH!")
    except Exception as e2:
        print(f"FAILED: {e2}")
        
        print("\n" + "=" * 60)
        print("MISSING DEPENDENCIES")
        print("=" * 60)
        print("\nThe DLL requires other DLL files that are missing.")
        print("\nCommon missing dependencies for RFID readers:")
        print("  - msvcr100.dll / msvcr120.dll / msvcr140.dll")
        print("  - msvcp100.dll / msvcp120.dll / msvcp140.dll")
        print("  - vcruntime140.dll")
        print("  - api-ms-win-*.dll")
        print("\nSOLUTIONS:")
        print("1. Install Visual C++ Redistributable:")
        print("   https://aka.ms/vs/17/release/vc_redist.x64.exe")
        print("\n2. Copy missing DLLs to project directory")
        print("\n3. Use Dependency Walker to identify missing DLLs:")
        print("   https://www.dependencywalker.com/")

print("\n" + "=" * 60)
print("SYSTEM INFO")
print("=" * 60)
print(f"Python: {sys.version}")
print(f"Architecture: {sys.maxsize > 2**32 and '64-bit' or '32-bit'}")
print(f"Current directory: {os.getcwd()}")

input("\nPress ENTER to exit...")

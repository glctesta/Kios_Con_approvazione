"""
Simple RFID DLL Test Script
"""

import ctypes
import os


print("=" * 60)
print("TEST LETTORE RFID - IDReader.dll")
print("=" * 60)

dll_path = 'C:\\Users\\gtesta\\PythonProjetcs\\Python\\Adeverente\\IDReader.dll'

# Check if DLL exists
if not os.path.exists(dll_path):
    print(f"ERROR: {dll_path} not found")
    print(f"Current directory: {os.getcwd()}")
    input("Press ENTER to exit...")
    exit(1)

print(f"OK: Found {dll_path}")
print(f"Size: {os.path.getsize(dll_path)} bytes")

# Try to load DLL
try:
    dll = ctypes.WinDLL(dll_path)
    print("OK: DLL loaded successfully (WinDLL)")
except Exception as e:
    print(f"ERROR loading WinDLL: {e}")
    try:
        dll = ctypes.CDLL(dll_path)
        print("OK: DLL loaded successfully (CDLL)")
    except Exception as e2:
        print(f"ERROR loading CDLL: {e2}")
        input("Press ENTER to exit...")
        exit(1)

print("\n" + "=" * 60)
print("Testing common RFID functions...")
print("=" * 60)

# List of common function names
functions_to_test = [
    'OpenPort', 'Open', 'Connect', 'Initialize',
    'ClosePort', 'Close', 'Disconnect',
    'ReadCard', 'Read', 'GetCardID', 'GetID',
    'WriteCard', 'Write',
    'GetVersion', 'Beep'
]

found = []
for func_name in functions_to_test:
    try:
        func = getattr(dll, func_name)
        found.append(func_name)
        print(f"  FOUND: {func_name}")
    except AttributeError:
        pass

if found:
    print(f"\nTotal functions found: {len(found)}")
    print("\nFunctions list:")
    for f in found:
        print(f"  - {f}")
else:
    print("\nNo common functions found")
    print("The DLL might use different function names")

print("\n" + "=" * 60)
print("CONCLUSION")
print("=" * 60)

if found:
    print("SUCCESS: DLL loaded and functions found")
    print("\nNext steps:")
    print("1. Get documentation for correct parameters")
    print("2. Test with hardware connected")
    print("3. Update rfid_reader.py")
else:
    print("WARNING: DLL loaded but no common functions found")
    print("\nNext steps:")
    print("1. Get IDReader.dll documentation")
    print("2. Use 'dumpbin /EXPORTS IDReader.dll' to see all functions")

print("=" * 60)
input("\nPress ENTER to exit...")

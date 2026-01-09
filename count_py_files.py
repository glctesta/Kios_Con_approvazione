"""
Conta quanti file .py sono nel ZIP
"""
import zipfile
from glob import glob
import os

zip_files = glob("Kiosk_HR_v2.2.0_*.zip")
latest_zip = max(zip_files, key=os.path.getmtime)

with zipfile.ZipFile(latest_zip, 'r') as zipf:
    all_files = zipf.namelist()
    py_root = [f for f in all_files if f.endswith('.py') and '/' not in f]
    
    print(f"ZIP: {os.path.basename(latest_zip)}")
    print(f"File .py nella root: {len(py_root)}")
    print(f"File .py totali: {len([f for f in all_files if f.endswith('.py')])}")
    print(f"Totale file: {len(all_files)}")
    print(f"Dimensione: {os.path.getsize(latest_zip) / (1024*1024):.2f} MB")
    
    # Elenca i file .py
    print("\nFile Python nella root:")
    for f in sorted(py_root):
        print(f"  - {f}")

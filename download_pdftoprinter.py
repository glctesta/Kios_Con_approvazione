"""Scarica PDFtoPrinter.exe da mirror alternativo"""
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# Prova da vari mirror
mirrors = [
    ("GitHub Direct", "https://objects.githubusercontent.com/github-production-release-asset-2e65be/10398519/bb0b73f2-a8fa-11e5-8e44-3df2fb6e1679?X-Amz-Algorithm=AWS4-HMAC-SHA256"),
    ("Alternative CDN", "https://github.com/stchan/PDFtoPrinter/raw/master/Releases/PDFtoPrinter.exe"),
]

output = "PDFtoPrinter.exe"

for name, url in mirrors:
    print(f"\n📥 Tentativo download da: {name}")
    print(f"URL: {url[:80]}...")
    
    try:
        urllib.request.urlretrieve(url, output)
        
        import os
        size = os.path.getsize(output)
        
        if size > 50000:  # File valido
            print(f"✅ Download completato!")
            print(f"📁 File: {output}")
            print(f"📊 Dimensione: {size/1024:.1f} KB")
            break
        else:
            print(f"⚠️ File troppo piccolo ({size} bytes), provo altro mirror...")
            os.remove(output)
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        continue
else:
    print("\n❌ Tutti i mirror hanno fallito")
    print("\n📝 DOWNLOAD MANUALE NECESSARIO:")
    print("1. Apri browser: https://github.com/stchan/PDFtoPrinter")
    print("2. Vai su 'Releases' (menu laterale)")
    print("3. Scarica 'PDFtoPrinter.exe' dall'ultima release")
    print("4. Copia il file in:")
    print(f"   C:\\Users\\gtesta\\PythonProjetcs\\Python\\Adeverente\\PDFtoPrinter.exe")

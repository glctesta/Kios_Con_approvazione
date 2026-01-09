"""
Script per testare l'endpoint /api/news del server
"""
import requests
import json

url = "http://localhost:5000/api/news"

print("=" * 80)
print("TEST ENDPOINT /api/news")
print("=" * 80)
print(f"\nChiamata GET a: {url}")

try:
    response = requests.get(url, timeout=5)
    
    print(f"\nStatus Code: {response.status_code}")
    print("-" * 80)
    
    if response.status_code == 200:
        data = response.json()
        print("Risposta JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if data.get('success'):
            if data.get('has_news'):
                print(f"\n✓ News trovate: {len(data.get('news', []))}")
                for idx, news in enumerate(data.get('news', []), 1):
                    print(f"\nNews #{idx}:")
                    print(f"  Messaggio: {news.get('message', '')[:100]}")
                    print(f"  Publisher: {news.get('publisher', '')}")
                    print(f"  Mandatory: {news.get('is_mandatory', False)}")
            else:
                print("\n✗ Nessuna news trovata dal server")
                print("POSSIBILI CAUSE:")
                print("  1. Il server usa ancora il vecchio codice (riavviare)")
                print("  2. La query SQL non funziona correttamente")
                print("  3. Le news nel database sono scadute")
        else:
            print(f"\n✗ Errore dal server: {data.get('error', 'Sconosciuto')}")
    else:
        print(f"✗ Errore HTTP: {response.status_code}")
        print(f"Risposta: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n✗ ERRORE: Impossibile connettersi al server")
    print("Il server su http://localhost:5000 non risponde")
    print("\nAvviare il server con: python app.py")
    
except requests.exceptions.Timeout:
    print("\n✗ ERRORE: Timeout della richiesta")
    
except Exception as e:
    print(f"\n✗ ERRORE: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)

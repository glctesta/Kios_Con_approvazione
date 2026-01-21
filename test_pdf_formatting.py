"""
Test formattazione PDF news - Verifica split paragrafi
"""
import re

# Esempio testi da database
test_texts = [
    "Bun Lunes. Sper a treaba. Hau a good working talk.",
    "Comunicazione importante della direzione. Si prega di prendere nota. Grazie per la collaborazione.",
    "Test senza punti solo virgole, e altri segni",
    "Test! Con esclamativi! E interrogativi? Funziona?"
]

for i, text in enumerate(test_texts, 1):
    print(f"\n{'='*60}")
    print(f"TEST {i}: {text[:50]}...")
    print('='*60)
    
    # Split su punteggiatura (.!?) seguita da spazio
    sentence_endings = re.split(r'([.!?])\s+', text)
    
    sentences = []
    for j in range(0, len(sentence_endings)-1, 2):
        if sentence_endings[j].strip():
            sentence = sentence_endings[j].strip() + sentence_endings[j+1]
            sentences.append(sentence)
    
    # Aggiungi ultima parte se non termina con punteggiatura
    if len(sentence_endings) % 2 == 1 and sentence_endings[-1].strip():
        sentences.append(sentence_endings[-1].strip())
    
    print(f"\nTrovate {len(sentences)} frasi:")
    for idx, s in enumerate(sentences, 1):
        print(f"  {idx}. {s}")
    
    # Simula output con spazi
    print("\nOutput formattato:")
    for idx, s in enumerate(sentences):
        print(f"  {s}")
        if idx < len(sentences) - 1:
            print("  [SPAZIO PARAGRAFO]")

print(f"\n{'='*60}")
print("✅ Test completato")

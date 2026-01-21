"""
Test completo generazione PDF con formattazione paragrafi
"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
import re

# Registra font
registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

# Crea PDF di test
pdf_file = "test_formattazione.pdf"
c = canvas.Canvas(pdf_file, pagesize=A4)
width, height = A4

# Testo di test
news_text = "Bun Lunes. Sper a treaba. Hau a good working talk. This is another sentence with more text. And one more for testing purposes."

# Setup
font_name = 'DejaVuSans'
c.setFont(font_name, 24)
c.drawString(30*mm, height - 20*mm, "Test Formattazione PDF")

y_pos = height - 40*mm
c.setFont(font_name, 18)

# Margini
left_margin = 35*mm
max_width = width - 70*mm

# Split testo su punteggiatura
sentence_endings = re.split(r'([.!?])\s+', news_text)

sentences = []
for i in range(0, len(sentence_endings)-1, 2):
    if sentence_endings[i].strip():
        sentence = sentence_endings[i].strip() + sentence_endings[i+1]
        sentences.append(sentence)

if len(sentence_endings) % 2 == 1 and sentence_endings[-1].strip():
    sentences.append(sentence_endings[-1].strip())

print(f"✅ Trovate {len(sentences)} frasi")

# Word wrap per ogni frase
lines = []
for idx, sentence in enumerate(sentences):
    words = sentence.split()
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if c.stringWidth(test_line, font_name, 18) <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    if idx < len(sentences) - 1:
        lines.append('PARAGRAPH_BREAK')

print(f"✅ Formattate {len(lines)} righe")

# Stampa linee
line_height = 6.5*mm
paragraph_spacing = 3*mm

paragraph_count = 0
for line in lines:
    if line == 'PARAGRAPH_BREAK':
        y_pos -= paragraph_spacing
        paragraph_count += 1
        print(f"  📍 Spazio paragrafo #{paragraph_count}")
    else:
        c.drawString(left_margin, y_pos, line)
        y_pos -= line_height
        print(f"  📝 {line}")

c.save()
print(f"\n✅ PDF generato: {pdf_file}")
print(f"📊 Statistiche:")
print(f"   - Frasi: {len(sentences)}")
print(f"   - Righe totali: {len(lines)}")
print(f"   - Spazi paragrafo: {paragraph_count}")

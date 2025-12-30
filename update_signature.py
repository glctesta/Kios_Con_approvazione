"""
Utility per aggiornare la firma dell'amministratore nel database
Permette di caricare una nuova immagine firma (PNG, JPG, BMP)
"""
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import io
import json
import pyodbc
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignatureUpdater:
    def __init__(self, root):
        self.root = root
        self.root.title("Aggiorna Firma Amministratore")
        self.root.geometry("600x800")
        self.root.resizable(False, False)
        
        # Variabili
        self.config_manager = None
        self.db_config = None
        self.conn = None
        self.current_signature = None
        self.new_signature_path = None
        
        # Carica configurazione database
        self.load_db_config()
        
        # Crea interfaccia
        self.create_widgets()
        
        # Carica firma corrente
        self.load_current_signature()
    
    def load_db_config(self):
        """Carica configurazione database usando ConfigManager"""
        try:
            from config_manager import ConfigManager
            self.config_manager = ConfigManager()
            self.db_config = self.config_manager.load_config()
            logger.info("Configurazione database caricata")
        except Exception as e:
            messagebox.showerror("Errore", 
                f"Impossibile caricare configurazione database:\n{str(e)}\n\n"
                f"Assicurati che il file db_config.enc esista.")
            sys.exit(1)
    
    def connect_db(self):
        """Connetti al database"""
        try:
            if self.conn:
                return self.conn
            
            # Usa DatabaseConnection come nell'app principale
            from db_connection import DatabaseConnection
            db_connection = DatabaseConnection(self.config_manager)
            self.conn = db_connection.connect()
            
            logger.info("Connesso al database")
            return self.conn
            
        except Exception as e:
            messagebox.showerror("Errore", f"Connessione database fallita:\n{str(e)}")
            return None
    
    def create_widgets(self):
        """Crea interfaccia grafica"""
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titolo
        title = ttk.Label(main_frame, text="Gestione Firma Amministratore", 
                         font=('Arial', 16, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Sezione firma corrente
        ttk.Label(main_frame, text="Firma Corrente:", font=('Arial', 12, 'bold')).grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Canvas per mostrare firma corrente
        self.current_canvas = tk.Canvas(main_frame, width=400, height=150, 
                                       bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.current_canvas.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        # Info firma corrente
        self.current_info = ttk.Label(main_frame, text="Caricamento...", 
                                     foreground='gray')
        self.current_info.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        # Sezione nuova firma
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        
        ttk.Label(main_frame, text="Nuova Firma:", font=('Arial', 12, 'bold')).grid(
            row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Bottone seleziona file
        btn_select = ttk.Button(main_frame, text="📁 Seleziona Immagine Firma", 
                               command=self.select_signature_file)
        btn_select.grid(row=6, column=0, columnspan=2, pady=(0, 10))
        
        # Canvas per preview nuova firma
        self.new_canvas = tk.Canvas(main_frame, width=400, height=150, 
                                   bg='#f0f0f0', relief=tk.SUNKEN, borderwidth=2)
        self.new_canvas.grid(row=7, column=0, columnspan=2, pady=(0, 10))
        
        # Info nuova firma
        self.new_info = ttk.Label(main_frame, text="Nessuna immagine selezionata", 
                                 foreground='gray')
        self.new_info.grid(row=8, column=0, columnspan=2, pady=(0, 20))
        
        # Bottoni azione
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=9, column=0, columnspan=2, pady=(10, 0))
        
        self.btn_update = ttk.Button(btn_frame, text="✅ Aggiorna Firma", 
                                     command=self.update_signature, state=tk.DISABLED)
        self.btn_update.grid(row=0, column=0, padx=5)
        
        btn_cancel = ttk.Button(btn_frame, text="❌ Annulla", command=self.root.quit)
        btn_cancel.grid(row=0, column=1, padx=5)
    
    def load_current_signature(self):
        """Carica e mostra firma corrente dal database"""
        try:
            conn = self.connect_db()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # Query firma amministratore
            query = """
            SELECT [Signature], [EmployeeName], [EmployeeSurname]
            FROM [Employee].[dbo].[Administrators] 
            INNER JOIN [Employee].[dbo].[Employees] 
                ON [Administrators].[EmployeeID] = [Employees].[EmployeeId]
            WHERE [Administrators].adminid = 3
            """
            
            cursor.execute(query)
            row = cursor.fetchone()
            
            if row and row[0]:
                # Converti BLOB in immagine
                self.current_signature = row[0]
                img = Image.open(io.BytesIO(self.current_signature))
                
                # Ridimensiona per canvas
                img.thumbnail((380, 130), Image.Resampling.LANCZOS)
                
                # Converti per Tkinter
                from PIL import ImageTk
                self.current_photo = ImageTk.PhotoImage(img)
                
                # Mostra su canvas
                self.current_canvas.create_image(200, 75, image=self.current_photo)
                
                # Info
                admin_name = f"{row[1]} {row[2]}"
                size_kb = len(self.current_signature) / 1024
                self.current_info.config(
                    text=f"Amministratore: {admin_name} | Dimensione: {size_kb:.1f} KB",
                    foreground='green'
                )
                
                logger.info(f"Firma corrente caricata: {admin_name}")
            else:
                self.current_canvas.create_text(200, 75, 
                    text="Nessuna firma trovata nel database", 
                    fill='red', font=('Arial', 12))
                self.current_info.config(text="Firma non presente", foreground='red')
                
        except Exception as e:
            logger.error(f"Errore caricamento firma: {str(e)}")
            self.current_canvas.create_text(200, 75, 
                text=f"Errore: {str(e)}", fill='red')
            self.current_info.config(text="Errore caricamento", foreground='red')
    
    def select_signature_file(self):
        """Seleziona file immagine firma"""
        filetypes = (
            ('Immagini', '*.png *.jpg *.jpeg *.bmp'),
            ('PNG', '*.png'),
            ('JPEG', '*.jpg *.jpeg'),
            ('Tutti i file', '*.*')
        )
        
        filename = filedialog.askopenfilename(
            title='Seleziona immagine firma',
            filetypes=filetypes
        )
        
        if filename:
            try:
                # Carica immagine
                img = Image.open(filename)
                
                # Converti in RGB se necessario
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Salva path
                self.new_signature_path = filename
                
                # Preview
                preview_img = img.copy()
                preview_img.thumbnail((380, 130), Image.Resampling.LANCZOS)
                
                from PIL import ImageTk
                self.new_photo = ImageTk.PhotoImage(preview_img)
                
                # Mostra su canvas
                self.new_canvas.delete("all")
                self.new_canvas.create_image(200, 75, image=self.new_photo)
                
                # Info
                size_kb = os.path.getsize(filename) / 1024
                self.new_info.config(
                    text=f"File: {os.path.basename(filename)} | {img.width}x{img.height}px | {size_kb:.1f} KB",
                    foreground='blue'
                )
                
                # Abilita bottone aggiorna
                self.btn_update.config(state=tk.NORMAL)
                
                logger.info(f"Nuova firma selezionata: {filename}")
                
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile caricare immagine:\n{str(e)}")
                self.new_signature_path = None
                self.btn_update.config(state=tk.DISABLED)
    
    def update_signature(self):
        """Aggiorna firma nel database"""
        if not self.new_signature_path:
            messagebox.showwarning("Attenzione", "Seleziona prima un'immagine!")
            return
        
        # Conferma
        if not messagebox.askyesno("Conferma", 
            "Sei sicuro di voler aggiornare la firma dell'amministratore?\n\n"
            "Questa operazione sostituirà la firma corrente nel database."):
            return
        
        try:
            # Carica immagine
            img = Image.open(self.new_signature_path)
            
            # Converti in RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Converti in bytes (PNG)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            signature_blob = img_bytes.getvalue()
            
            # Aggiorna database
            conn = self.connect_db()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            update_query = """
            UPDATE [Employee].[dbo].[Administrators]
            SET [Signature] = ?
            WHERE adminid = 3
            """
            
            cursor.execute(update_query, (signature_blob,))
            conn.commit()
            
            logger.info("Firma aggiornata nel database")
            
            messagebox.showinfo("Successo", 
                "Firma aggiornata con successo!\n\n"
                "La nuova firma sarà utilizzata nei prossimi certificati generati.")
            
            # Ricarica firma corrente
            self.load_current_signature()
            
            # Reset nuova firma
            self.new_canvas.delete("all")
            self.new_signature_path = None
            self.new_info.config(text="Nessuna immagine selezionata", foreground='gray')
            self.btn_update.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"Errore aggiornamento firma: {str(e)}")
            messagebox.showerror("Errore", f"Impossibile aggiornare firma:\n{str(e)}")
    
    def __del__(self):
        """Chiudi connessione database"""
        if self.conn:
            self.conn.close()


def main():
    """Funzione principale"""
    root = tk.Tk()
    app = SignatureUpdater(root)
    root.mainloop()


if __name__ == "__main__":
    main()

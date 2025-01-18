import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# Veritabanı bağlantısı
def connect_database():
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note TEXT NOT NULL,
        category TEXT,
        reminder DATETIME
    )
    """)
    conn.commit()
    conn.close()

# Tarih ve saat doğrulama
def validate_reminder(reminder):
    try:
        if len(reminder) == 10:  # YYYY-MM-DD formatı
            reminder = reminder + " 00:00:00"  # Eğer sadece tarih verilmişse saati 00:00:00 olarak ekle
        reminder_time = datetime.strptime(reminder, "%Y-%m-%d %H:%M:%S")
        return reminder_time
    except ValueError:
        messagebox.showwarning("Hata", "Geçersiz tarih/saat formatı! Lütfen 'YYYY-MM-DD HH:MM:SS' formatında giriniz.")
        return None

# Notları veritabanına ekleme
def add_note():
    note = note_text.get("1.0", tk.END).strip()
    category = category_entry.get().strip()
    reminder = reminder_entry.get().strip()

    if not note:
        messagebox.showwarning("Uyarı", "Not içeriği boş olamaz!")
        return

    reminder_time = validate_reminder(reminder)
    if reminder_time is None:
        return

    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (note, category, reminder) VALUES (?, ?, ?)", (note, category, reminder_time))
    conn.commit()
    conn.close()

    note_text.delete("1.0", tk.END)
    category_entry.delete(0, tk.END)
    reminder_entry.delete(0, tk.END)
    messagebox.showinfo("Başarılı", "Not eklendi!")
    display_notes()

# Notları listeleme
def display_notes():
    notes_list.delete(0, tk.END)
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, note, category, reminder FROM notes")
    notes = cursor.fetchall()
    conn.close()

    for note in notes:
        note_display = f"ID: {note[0]} | {note[1]} | Kategori: {note[2]} | Hatırlatma: {note[3]}"
        notes_list.insert(tk.END, note_display)

# Notları silme
def delete_note():
    selected_note = notes_list.curselection()
    if not selected_note:
        messagebox.showwarning("Uyarı", "Lütfen silmek için bir not seçin!")
        return

    note_id = notes_list.get(selected_note).split("|")[0].split(":")[1].strip()
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()

    messagebox.showinfo("Başarılı", "Not silindi!")
    display_notes()

# Hatırlatıcı kontrolü ve mesaj gösterme
def check_reminders():
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT note, reminder FROM notes WHERE reminder IS NOT NULL")
    notes = cursor.fetchall()
    conn.close()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for note, reminder in notes:
        if reminder and reminder <= now:
            messagebox.showinfo("Hatırlatma", f"Hatırlatma: {note}")
            # Hatırlatmayı sıfırlama
            conn = sqlite3.connect("notes.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE notes SET reminder=NULL WHERE reminder=?", (reminder,))
            conn.commit()
            conn.close()

# Periyodik hatırlatıcı kontrolü
def periodic_check():
    check_reminders()  # Hatırlatıcıları kontrol et
    root.after(60000, periodic_check)  # 60 saniyede bir tekrarla (60000 ms)

# Arayüz oluşturma
def create_ui():
    global note_text, category_entry, reminder_entry, notes_list, root

    # Ana pencere
    root = tk.Tk()
    root.title("Hızlı Not Alma ve Hatırlatma Uygulaması")
    root.geometry("600x400")

    # Not ekleme alanı
    tk.Label(root, text="Not:").pack()
    note_text = tk.Text(root, height=5, width=50)
    note_text.pack()

    tk.Label(root, text="Kategori (isteğe bağlı):").pack()
    category_entry = tk.Entry(root, width=50)
    category_entry.pack()

    tk.Label(root, text="Hatırlatma (YYYY-MM-DD HH:MM:SS) Örnek( 2025-01-25 15:30:00):").pack()
    reminder_entry = tk.Entry(root, width=50)
    reminder_entry.pack()

    tk.Button(root, text="Not Ekle", command=add_note).pack()

    # Not listesi
    tk.Label(root, text="Kayıtlı Notlar:").pack()
    notes_list = tk.Listbox(root, height=10, width=80)
    notes_list.pack()

    tk.Button(root, text="Not Sil", command=delete_note).pack()

    # Alt kısmına "Bu uygulama Ensar tarafından geliştirilmiştir" yazısı ekleniyor
    tk.Label(root, text="Bu uygulama Ensar tarafından geliştirilmiştir", font=("Arial", 10), fg="gray").pack(side="bottom", pady=5)

    # Notları listele
    display_notes()

    # Periyodik hatırlatıcı kontrolüne başla
    periodic_check()

    root.mainloop()

# Program başlangıcı
if __name__ == "__main__":
    connect_database()
    create_ui()

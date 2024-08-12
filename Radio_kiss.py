import tkinter as tk
from tkinter import PhotoImage
import threading
import webview
import requests
from bs4 import BeautifulSoup

# Globální proměnné
webview_window = None
root = None  # Tento root bude definován v create_tk_window

# URL stránky, kde se zobrazuje aktuální písnička
url = 'https://www.kiss.cz/online/'

def fetch_current_track():
    """Získá aktuální název písničky a interpreta ze stránky."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Zkontroluje, zda byl požadavek úspěšný

        # Parsování HTML obsahu stránky
        soup = BeautifulSoup(response.content, 'html.parser')

        # Vyhledání názvu písničky a interpreta
        song = soup.find('p', class_='song').text.strip()
        artist = soup.find('p', class_='artist').text.strip()

        return song, artist
    except Exception as e:
        print(f"Chyba při získávání aktuální písničky: {e}")
        return None, None

def update_track_info():
    """Aktualizuje text labelu s informacemi o aktuální písničce."""
    song, artist = fetch_current_track()
    if song and artist:
        track_info_label.config(text=f"{song} \n {artist}")
    else:
        track_info_label.config(text="Nepodařilo se získat informace o aktuální písničce.")
    
    # Aktualizuje informace každých 30 sekund
    root.after(30000, update_track_info)

def create_tk_window():
    global root, track_info_label
    
    root = tk.Tk()
    root.geometry("300x150")
    root.overrideredirect(True)  # Odstraní rámeček a lišty
    root.config(bg="red")

    # Nastavení pozice okna na střed obrazovky
    root.update_idletasks()  # Aktualizuje geometrii okna
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    # Funkce pro přesun hlavního okna
    def start_move(event):
        global x_offset, y_offset
        x_offset = event.x
        y_offset = event.y

    def stop_move(event):
        global x_offset, y_offset
        x_offset = None
        y_offset = None

    def on_motion(event):
        x = root.winfo_pointerx() - x_offset
        y = root.winfo_pointery() - y_offset
        root.geometry(f'+{x}+{y}')

    # Funkce pro zavření hlavního okna a webview okna
    def close_window(event=None):
        root.destroy()  # Zavře hlavní okno
        if webview_window:
            webview_window.destroy()  # Zavře skryté webview okno

    # Tlačítko pro zavření okna
    close_button = tk.Button(root, text="X ", bg="black", fg="white", relief="flat", command=close_window)
    close_button.place(x=283, y=0)

    # Velký text "Rádio KISS"
    title_label = tk.Label(root, text="Rádio KISS", font=("Arial", 24, "bold"), fg="white", bg="red")
    title_label.pack(pady=(10, 0))  # Přidání odsazení nad text

    # Label pro zobrazení textu s aktuální písničkou
    track_info_label = tk.Label(root, text="Načítání...", font=("Arial", 12), fg="white", bg="red")
    track_info_label.pack(expand=True)

    # Přidání událostí pro přesun okna
    root.bind("<ButtonPress-1>", start_move)
    root.bind("<ButtonRelease-1>", stop_move)
    root.bind("<B1-Motion>", on_motion)

    # Spuštění aktualizace informací o písničce
    update_track_info()

    # Spuštění hlavní smyčky Tkinter
    root.mainloop()

def start_webview():
    global webview_window
    webview_window = webview.create_window(
        "Rádio KISS", 
        "https://n10a-eu.rcs.revma.com/asn0cmvb938uv?rj-ttl=5&rj-tok=AAABkUe5PvQAzSwu4DWRtCDOCw",
        width=250, height=100, hidden=False
    )
    
    def hide_window():
        webview_window.move(-3000, -3000)  # Přesune okno mimo viditelnou oblast
    
    # Nastavení časovače pro skrytí okna po 1 sekundě
    threading.Timer(1, hide_window).start()
    
    webview.start()

# Vytvoření vlákna pro Tkinter
tk_thread = threading.Thread(target=create_tk_window, daemon=True)
tk_thread.start()

# Spuštění webview na hlavním vlákně
start_webview()

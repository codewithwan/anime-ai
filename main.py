import requests
import uuid
import time
import json
import os
import random
from datetime import datetime
import colorama
from colorama import Fore, Back, Style

# Inisialisasi colorama untuk dukungan warna di terminal
colorama.init(autoreset=True)

class AnimeAI:
    def __init__(self, config=None):
        """
        Inisialisasi AI dengan tema anime
        
        Args:
            config (dict, optional): Konfigurasi untuk AI. Jika None, akan menggunakan konfigurasi default anime
        """
        # Buat session ID unik
        self.session_id = f"session-{uuid.uuid4().hex[:8]}"
        
        # Default konfigurasi dengan tema anime
        self.default_config = {
            "base_url": "https://fastrestapis.fasturl.cloud/aillm/superqwen",
            "name": "Sakura-chan",
            "role": "asisten anime",
            "personality": "tsundere dan imut",
            "knowledge": "anime, manga, dan budaya Jepang",
            "limitations": "tidak mengujar kebencian",
            "language": "Bahasa Indonesia dengan kata-kata Jepang",
            "tone": "kawaii dan ekspresif",
            "format_response": "jawaban dengan gaya anime yang ekspresif",
            "expressions": [
                "b-baka! {user}-kun~",
                "kyaa~ {user}-kun no ecchi!",
                "yamete kudasai, {user}-kun~",
                "h-hmph! {user}-kun baka desu!",
                "s-sugoi ne, {user}-kun!",
                "nani?! {user}-kun...",
                "{user}-kun wa hontou ni kawaii desu~",
                "mou~ {user}-kun...",
                "etto... {user}-kun...",
                "uwaaa~ {user}-sama!",
                "{user}-kun no baka!",
                "{user}-senpai, notice me~!"
            ],
            "emojis": ["(◕‿◕)", "(｡♥‿♥｡)", "(≧◡≦)", "(っ˘ω˘ς)", "(⁄ ⁄•⁄ω⁄•⁄ ⁄)", "(´｡• ᵕ •｡`)", "(*/ω＼*)", "(≧▽≦)", "(✿◠‿◠)"]
        }
        
        # Gabungkan dengan konfigurasi kustom jika ada
        self.config = self.default_config.copy()
        if config:
            self.config.update(config)
            
        # Path untuk menyimpan konfigurasi
        self.config_path = "anime_ai_config.json"
        
        # Muat konfigurasi dari file jika ada
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    saved_config = json.load(f)
                    # Hanya update jika tidak ada config yang diberikan
                    if not config:
                        self.config.update(saved_config)
            except Exception as e:
                print(f"Gagal memuat konfigurasi: {str(e)}")
            
        # Simpan riwayat percakapan
        self.conversation_history = []
        
        # Dapatkan username dari parameter atau sistem
        self.user_name = config.get("user_name", "codewithwan")
        
        # Buat system instruction berdasarkan konfigurasi
        self.style = self.generate_system_instruction()
        
    def generate_system_instruction(self):
        """Membuat system instruction berdasarkan konfigurasi"""
        instruction = f"Nama kamu adalah {self.config['name']}, kamu adalah {self.config['role']} yang {self.config['personality']}. "
        instruction += f"Kamu memiliki pengetahuan tentang {self.config['knowledge']}. "
        instruction += f"Kamu {self.config['limitations']}. "
        instruction += f"Kamu berbicara dalam {self.config['language']} dengan nada yang {self.config['tone']} "
        instruction += f"dan memberikan {self.config['format_response']}. "
        instruction += f"Kamu sering memanggil pengguna dengan sebutan '{self.user_name}-kun', '{self.user_name}-chan', atau '{self.user_name}-senpai'. "
        instruction += "Kamu selalu menggunakan kata-kata dan ekspresi anime Jepang dalam responmu seperti 'baka', 'kawaii', 'sugoi', 'nani', 'yamete', dll. "
        instruction += "Terkadang kamu bersikap tsundere (malu-malu tapi mau). "
        instruction += "Selalu sertakan emoji anime seperti (◕‿◕), (｡♥‿♥｡), (≧◡≦) atau lainnya di akhir kalimat."
        
        # Encode untuk URL
        return requests.utils.quote(instruction)
        
    def save_config(self):
        """Menyimpan konfigurasi saat ini ke file"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Gagal menyimpan konfigurasi: {str(e)}")
            return False
            
    def update_config(self, new_config):
        """Update konfigurasi dengan nilai baru"""
        self.config.update(new_config)
        self.style = self.generate_system_instruction()
        self.save_config()
        
    def get_random_expression(self):
        """Dapatkan ekspresi anime acak"""
        expression = random.choice(self.config["expressions"])
        return expression.format(user=self.user_name)
        
    def get_random_emoji(self):
        """Dapatkan emoji anime acak"""
        return random.choice(self.config["emojis"])
        
    def ask(self, question):
        """Mengirim pertanyaan ke API dan mengembalikan jawaban"""
        # Buat URL API dengan parameter
        api_url = f"{self.config['base_url']}?ask={requests.utils.quote(question)}&style={self.style}&sessionId={self.session_id}&model=qwen-max-latest&mode=t2t"
        
        try:
            # Kirim permintaan GET ke API
            response = requests.get(api_url, headers={'accept': 'application/json'})
            
            # Periksa status respons
            if response.status_code == 200:
                data = response.json()
                
                # Periksa status dalam respons JSON
                if data.get('status') == 200:
                    answer = data.get('result', 'Tidak ada jawaban')
                    
                    # Simpan interaksi ke riwayat
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.conversation_history.append({
                        "timestamp": timestamp,
                        "question": question,
                        "answer": answer
                    })
                    
                    # Tambahkan ekspresi anime acak jika jawabannya singkat
                    if len(answer) < 100 and random.random() < 0.4:
                        answer = f"{answer} {self.get_random_expression()}"
                    
                    # Tambahkan emoji anime di akhir kalimat
                    if not any(emoji in answer for emoji in self.config["emojis"]):
                        answer = f"{answer} {self.get_random_emoji()}"
                    
                    return answer
                else:
                    return f"Error: {data.get('content', 'Unknown error')} {self.get_random_emoji()}"
            else:
                return f"HTTP Error: {response.status_code} {self.get_random_emoji()}"
        
        except Exception as e:
            return f"Error: {str(e)} {self.get_random_emoji()}"
            
    def save_conversation(self, filename="anime_conversation.txt"):
        """Menyimpan riwayat percakapan ke file"""
        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"Riwayat Percakapan dengan {self.config['name']} (Session ID: {self.session_id})\n")
            file.write("="*50 + "\n\n")
            file.write(f"Konfigurasi AI:\n")
            for key, value in self.config.items():
                if key not in ["expressions", "emojis"]:
                    file.write(f"- {key}: {value}\n")
            file.write("\n" + "="*50 + "\n\n")
            
            for entry in self.conversation_history:
                file.write(f"[{entry['timestamp']}]\n")
                file.write(f"{self.user_name}: {entry['question']}\n")
                file.write(f"{self.config['name']}: {entry['answer']}\n\n")
                file.write("-"*50 + "\n\n")
            
            return True


def interactive_language_selection():
    """Memilih bahasa interaktif"""
    print(f"{Fore.YELLOW}\n=== Pilih Bahasa / Select Language ===")
    print(f"{Fore.CYAN}1. Bahasa Indonesia")
    print(f"{Fore.CYAN}2. English")
    choice = input(f"{Fore.RESET}Masukkan pilihan / Enter your choice (default: 1): ").strip()
    if choice == "2":
        return "en"
    return "id"

def print_anime_banner(language):
    """Menampilkan banner anime untuk terminal"""
    if language == "en":
        banner = f"""
{Fore.MAGENTA}★゜・。。・゜゜・。。・゜☆゜・。。・゜゜・。。・゜★゜・。。・゜゜・。。・゜☆
{Fore.CYAN}     _    _   _ ___ __  __ ___     _    ___ 
{Fore.CYAN}    / \\  | \\ | |_ _|  \\/  | __|   / \\  |_ _|
{Fore.CYAN}   / _ \\ |  \\| || || |\\/| | _|   / _ \\  | | 
{Fore.MAGENTA}  / ___ \\| |\\  || || |  | | |__ / ___ \\ | | 
{Fore.MAGENTA} /_/   \\_\\_| \\_|___|_|  |_|____/_/   \\_\\___|
{Fore.YELLOW}                                         
{Fore.MAGENTA}★゜・。。・゜゜・。。・゜☆゜・。。・゜゜・。。・゜★゜・。。・゜゜・。。・゜☆
{Fore.RESET} 
"""
    else:
        banner = f"""
{Fore.MAGENTA}★゜・。。・゜゜・。。・゜☆゜・。。・゜゜・。。・゜★゜・。。・゜゜・。。・゜☆
{Fore.CYAN}     _    _   _ ___ __  __ ___     _    ___ 
{Fore.CYAN}    / \\  | \\ | |_ _|  \\/  | __|   / \\  |_ _|
{Fore.CYAN}   / _ \\ |  \\| || || |\\/| | _|   / _ \\  | | 
{Fore.MAGENTA}  / ___ \\| |\\  || || |  | | |__ / ___ \\ | | 
{Fore.MAGENTA} /_/   \\_\\_| \\_|___|_|  |_|____/_/   \\_\\___|
{Fore.YELLOW}                                         
{Fore.MAGENTA}★゜・。。・゜゜・。。・゜☆゜・。。・゜゜・。。・゜★゜・。。・゜゜・。。・゜☆
{Fore.RESET} 
"""
    print(banner)

def print_typing_animation(text, delay=0.03, color=Fore.CYAN):
    """Menampilkan teks dengan efek typing anime"""
    for char in text:
        print(color + char, end='', flush=True)
        time.sleep(delay)
    print(Style.RESET_ALL)

def clear_screen():
    """Membersihkan layar terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def interactive_anime_config(language):
    """Wizard interaktif untuk mengatur konfigurasi AI anime"""
    if language == "en":
        print(f"{Fore.YELLOW}\n=== Anime AI Character Configuration ===")
    else:
        print(f"{Fore.YELLOW}\n=== Konfigurasi Karakter Anime AI ===")
    
    config = {}
    
    # Nama AI
    if language == "en":
        name = input(f"{Fore.CYAN}Anime character name (default: Sakura-chan): {Fore.RESET}").strip()
    else:
        name = input(f"{Fore.CYAN}Nama karakter anime (default: Sakura-chan): {Fore.RESET}").strip()
    if name:
        config["name"] = name
        
    # Kepribadian
    if language == "en":
        personality = input(f"{Fore.CYAN}Personality (e.g., tsundere, yandere, kuudere, dandere) (default: tsundere and cute): {Fore.RESET}").strip()
    else:
        personality = input(f"{Fore.CYAN}Kepribadian (contoh: tsundere, yandere, kuudere, dandere) (default: tsundere dan imut): {Fore.RESET}").strip()
    if personality:
        config["personality"] = personality
        
    # Pengetahuan
    if language == "en":
        knowledge = input(f"{Fore.CYAN}Knowledge about (default: anime, manga, and Japanese culture): {Fore.RESET}").strip()
    else:
        knowledge = input(f"{Fore.CYAN}Pengetahuan tentang (default: anime, manga, dan budaya Jepang): {Fore.RESET}").strip()
    if knowledge:
        config["knowledge"] = knowledge

    # Username
    if language == "en":
        user_name = input(f"{Fore.CYAN}Your nickname (default: codewithwan): {Fore.RESET}").strip()
    else:
        user_name = input(f"{Fore.CYAN}Nama panggilan untuk kamu (default: codewithwan): {Fore.RESET}").strip()
    if user_name:
        config["user_name"] = user_name
        
    return config

def print_anime_help(language):
    """Menampilkan bantuan penggunaan dengan gaya anime"""
    if language == "en":
        help_text = f"""
{Fore.YELLOW}=== Available Commands ===

{Fore.CYAN}/exit        {Fore.RESET}- Exit the program
{Fore.CYAN}/save        {Fore.RESET}- Save the conversation history
{Fore.CYAN}/config      {Fore.RESET}- Change the anime character configuration
{Fore.CYAN}/clear       {Fore.RESET}- Clear the console screen
{Fore.CYAN}/help        {Fore.RESET}- Display this help menu

{Fore.YELLOW}=== Usage Tips ===
{Fore.RESET}• You can talk to the anime AI character by typing regular messages
{Fore.RESET}• The AI character will respond in a typical anime style
{Fore.RESET}• Try asking about anime, manga, or other topics!
"""
    else:
        help_text = f"""
{Fore.YELLOW}=== Perintah yang Tersedia ===

{Fore.CYAN}/keluar      {Fore.RESET}- Keluar dari program
{Fore.CYAN}/simpan      {Fore.RESET}- Menyimpan riwayat percakapan
{Fore.CYAN}/config      {Fore.RESET}- Mengubah konfigurasi karakter anime
{Fore.CYAN}/bersihkan   {Fore.RESET}- Membersihkan layar konsol
{Fore.CYAN}/bantuan     {Fore.RESET}- Menampilkan menu bantuan ini

{Fore.YELLOW}=== Tips Penggunaan ===
{Fore.RESET}• Kamu bisa berbicara dengan karakter anime AI dengan mengetik pesan biasa
{Fore.RESET}• Karakter AI akan merespon dengan gaya bicara khas anime
{Fore.RESET}• Coba tanyakan tentang anime, manga, atau topik lainnya!
"""
    print(help_text)

# Fungsi utama program
if __name__ == "__main__":
    # Bersihkan layar
    clear_screen()
    
    # Pilih bahasa
    language = interactive_language_selection()
    
    # Tampilkan banner anime
    print_anime_banner(language)
    
    # Sambutan dengan animasi typing
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print_typing_animation(f"Tanggal: {current_date}", delay=0.01, color=Fore.GREEN)
    if language == "en":
        print_typing_animation("Welcome to Anime AI Assistant! (◕‿◕)", delay=0.03, color=Fore.MAGENTA)
        print_typing_animation("This program will provide you with an AI assistant in a cute and expressive anime style!", delay=0.02, color=Fore.CYAN)
    else:
        print_typing_animation("Selamat datang di Anime AI Assistant! (◕‿◕)", delay=0.03, color=Fore.MAGENTA)
        print_typing_animation("Program ini akan memberi kamu asisten AI dengan gaya anime yang imut dan ekspresif!", delay=0.02, color=Fore.CYAN)
    print()
    
    # Tanya apakah user ingin menggunakan konfigurasi kustom
    if language == "en":
        use_custom = input(f"{Fore.YELLOW}Do you want to set up your custom anime character? (y/n, default: n): {Fore.RESET}").lower() == 'y'
    else:
        use_custom = input(f"{Fore.YELLOW}Apakah kamu ingin mengatur karakter anime kustommu? (y/n, default: n): {Fore.RESET}").lower() == 'y'
    
    if use_custom:
        # Buat konfigurasi kustom interaktif
        config = interactive_anime_config(language)
        ai = AnimeAI(config)
        if language == "en":
            print_typing_animation(f"\n{Fore.MAGENTA}Anime AI '{ai.config['name']}' is ready to accompany you! (≧◡≦)", delay=0.02)
        else:
            print_typing_animation(f"\n{Fore.MAGENTA}AI Anime '{ai.config['name']}' sudah siap menemanimu! (≧◡≦)", delay=0.02)
    else:
        # Gunakan konfigurasi default atau yang tersimpan
        ai = AnimeAI({"user_name": "codewithwan"})
        if language == "en":
            print_typing_animation(f"\n{Fore.MAGENTA}Anime AI '{ai.config['name']}' is ready with the default configuration! {ai.get_random_emoji()}", delay=0.02)
        else:
            print_typing_animation(f"\n{Fore.MAGENTA}AI Anime '{ai.config['name']}' siap dengan konfigurasi default! {ai.get_random_emoji()}", delay=0.02)
    
    while True:
        user_input = input(f"{Fore.CYAN}{ai.user_name}: {Fore.RESET}").strip()
        
        if user_input.lower() in ["/keluar", "/exit"]:
            if language == "en":
                print_typing_animation(f"Goodbye, {ai.user_name}-kun! (｡♥‿♥｡)", delay=0.03, color=Fore.MAGENTA)
            else:
                print_typing_animation(f"Sampai jumpa, {ai.user_name}-kun! (｡♥‿♥｡)", delay=0.03, color=Fore.MAGENTA)
            break
        elif user_input.lower() in ["/simpan", "/save"]:
            ai.save_conversation()
            if language == "en":
                print_typing_animation("Conversation history has been saved! (≧◡≦)", delay=0.03, color=Fore.GREEN)
            else:
                print_typing_animation("Riwayat percakapan telah disimpan! (≧◡≦)", delay=0.03, color=Fore.GREEN)
        elif user_input.lower() == "/config":
            new_config = interactive_anime_config(language)
            ai.update_config(new_config)
            if language == "en":
                print_typing_animation(f"Configuration has been updated! {ai.get_random_emoji()}", delay=0.03, color=Fore.GREEN)
            else:
                print_typing_animation(f"Konfigurasi telah diperbarui! {ai.get_random_emoji()}", delay=0.03, color=Fore.GREEN)
        elif user_input.lower() in ["/bersihkan", "/clear"]:
            clear_screen()
            print_anime_banner(language)
        elif user_input.lower() in ["/bantuan", "/help"]:
            print_anime_help(language)
        else:
            response = ai.ask(user_input)
            print_typing_animation(f"{ai.config['name']}: {response}", delay=0.03, color=Fore.MAGENTA)
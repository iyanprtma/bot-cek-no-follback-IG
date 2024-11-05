import os
from dotenv import load_dotenv
import instaloader
import time

# Memuat variabel dari file .env
load_dotenv()
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
INSTAGRAM_BACKUP_CODE = os.getenv('INSTAGRAM_BACKUP_CODE')  # Backup code sebagai cadangan satu kali
SESSION_FILE = f".INSTALOADER_SESSION-{INSTAGRAM_USERNAME}"

# Inisialisasi instaloader untuk login ke Instagram
loader = instaloader.Instaloader()

# Fungsi untuk login ke Instagram dengan 2FA atau backup code
def login_instagram():
    try:
        # Cek apakah sesi login sudah ada
        if os.path.isfile(SESSION_FILE):
            loader.load_session_from_file(INSTAGRAM_USERNAME, SESSION_FILE)
            print("✅ Login berhasil menggunakan sesi yang disimpan.")
        else:
            print("🔑 Masuk menggunakan username dan password.")
            loader.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            print("✅ Login berhasil.")
            loader.save_session_to_file(SESSION_FILE)  # Simpan sesi login

    except instaloader.exceptions.TwoFactorAuthRequiredException:
        print("⚠️ Login gagal: Two-factor authentication required.")
        try:
            two_factor_code = input("Masukkan kode autentikasi dua faktor atau tekan Enter untuk menggunakan backup code: ")
            if not two_factor_code:
                print("🔒 Menggunakan backup code...")
                two_factor_code = INSTAGRAM_BACKUP_CODE  # Menggunakan backup code dari .env
            loader.two_factor_login(two_factor_code)
            loader.save_session_to_file(SESSION_FILE)
            print("✅ Login dengan 2FA atau backup code berhasil dan sesi disimpan.")
        except Exception as e:
            print(f"❌ Login dengan 2FA gagal: {e}")
            exit(1)

# Fungsi untuk menampilkan progres
def display_progress(current, total, prefix=''):
    percent = int((current / total) * 100)
    bar = f"[{'#' * (percent // 10)}{' ' * (10 - (percent // 10))}]"
    print(f"\r{prefix} {bar} {percent}%", end="")

# Fungsi untuk mendapatkan daftar pengikut dengan progres
def get_followers_with_progress(username):
    profile = instaloader.Profile.from_username(loader.context, username)
    followers = set()
    total_followers = profile.followers  # Total jumlah pengikut

    print(f"🔄 Mengambil daftar pengikut ({total_followers} total)...")
    for index, follower in enumerate(profile.get_followers(), start=1):
        followers.add(follower.username)
        display_progress(index, total_followers, prefix="Pengikut")

    print("\n✅ Selesai mengambil pengikut.")
    return followers

# Fungsi untuk mendapatkan daftar yang diikuti dengan progres
def get_following_with_progress(username):
    profile = instaloader.Profile.from_username(loader.context, username)
    following = set()
    total_following = profile.followees  # Total jumlah yang diikuti

    print(f"🔄 Mengambil daftar yang diikuti ({total_following} total)...")
    for index, followee in enumerate(profile.get_followees(), start=1):
        following.add(followee.username)
        display_progress(index, total_following, prefix="Mengikuti")

    print("\n✅ Selesai mengambil yang diikuti.")
    return following

# Fungsi untuk memeriksa siapa yang tidak follow-back
def check_non_followback():
    followers = get_followers_with_progress(INSTAGRAM_USERNAME)
    following = get_following_with_progress(INSTAGRAM_USERNAME)
    non_followback = following - followers  # Mengambil yang diikuti namun tidak mem-follow-back
    return non_followback

# Fungsi utama untuk menjalankan pengecekan
def main():
    # Login ke Instagram
    login_instagram()

    # Mengecek siapa yang tidak follow-back
    print("🔍 Sedang mencari siapa yang tidak melakukan follow-back...")
    non_followback = check_non_followback()

    if non_followback:
        print("🚫 Pengguna yang tidak mem-follow-back:")
        for user in non_followback:
            print(f"- {user}")
    else:
        print("🎉 Semua pengguna sudah mem-follow-back Anda!")

    # Logout atau selesai
    loader.close()  # Menutup sesi untuk keamanan
    print("✅ Sesi login telah diakhiri.")

if __name__ == '__main__':
    main()

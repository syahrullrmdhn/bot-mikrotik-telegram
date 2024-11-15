from librouteros import connect
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Konfigurasi MikroTik
host = '172.27.0.156'
username = 'admin'
password = 'syahrul'

# Konfigurasi Bot Telegram
telegram_token = 'Masukkan_API_TELEGRAM'  # Ganti dengan token bot Telegram Anda

# Koneksi ke MikroTik
try:
    api = connect(username=username, password=password, host=host)
    print("Koneksi berhasil ke perangkat MikroTik.")
except Exception as e:
    print(f"Gagal terkoneksi ke MikroTik: {e}")
    exit()

# Fungsi MikroTik
def add_ip_address(ip_address, interface):
    try:
        api(cmd='/ip/address/add', address=ip_address, interface=interface)
        return f"IP {ip_address} berhasil ditambahkan ke interface {interface}."
    except Exception as e:
        return f"Gagal menambahkan IP address: {e}"

def get_all_ip_addresses():
    try:
        ip_addresses = api(cmd='/ip/address/print')
        result = "Daftar IP address yang ada di MikroTik:\n"
        for ip in ip_addresses:
            result += f"IP: {ip['address']}, Interface: {ip['interface']}\n"
        return result
    except Exception as e:
        return f"Gagal menampilkan IP address: {e}"

def ping_ip(target_ip, count=4):
    try:
        ping_results = api(cmd='/ping', address=target_ip, count=count)
        result = f"Hasil ping ke {target_ip}:\n"
        for res in ping_results:
            result += f"Status: {res.get('status')}, Time: {res.get('time')} ms\n"
        return result
    except Exception as e:
        return f"Gagal melakukan ping ke {target_ip}: {e}"

def traceroute_ip(target_ip):
    try:
        traceroute_results = api(cmd='/tool/traceroute', address=target_ip)
        result = f"Hasil traceroute ke {target_ip}:\n"
        for hop in traceroute_results:
            result += f"Hop: {hop.get('hop')}, Address: {hop.get('address')}, Time: {hop.get('time')} ms\n"
        return result
    except Exception as e:
        return f"Gagal melakukan traceroute ke {target_ip}: {e}"

# Fungsi Handler untuk Bot Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Selamat datang di Bot Network Automation MikroTik!\nKetik /help untuk daftar perintah.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/add_ip <ip_address> <interface> - Tambah IP Address ke Interface\n"
        "/show_ip - Tampilkan Semua IP Address\n"
        "/ping <ip_address> <count> - Ping IP Address\n"
        "/traceroute <ip_address> - Traceroute IP Address"
    )

async def add_ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("Gunakan format: /add_ip <ip_address> <interface>")
    else:
        ip_address = context.args[0]
        interface = context.args[1]
        result = add_ip_address(ip_address, interface)
        await update.message.reply_text(result)

async def show_ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = get_all_ip_addresses()
    await update.message.reply_text(result)

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1:
        await update.message.reply_text("Gunakan format: /ping <ip_address> <count>")
    else:
        target_ip = context.args[0]
        count = int(context.args[1]) if len(context.args) > 1 else 4
        result = ping_ip(target_ip, count)
        await update.message.reply_text(result)

async def traceroute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1:
        await update.message.reply_text("Gunakan format: /traceroute <ip_address>")
    else:
        target_ip = context.args[0]
        result = traceroute_ip(target_ip)
        await update.message.reply_text(result)

# Menyiapkan Bot Telegram
def main():
    application = Application.builder().token(telegram_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add_ip", add_ip_command))
    application.add_handler(CommandHandler("show_ip", show_ip_command))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("traceroute", traceroute_command))

    application.run_polling()

if __name__ == '__main__':
    main()

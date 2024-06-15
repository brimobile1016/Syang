import os
import logging
from flask import Flask, render_template
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Cloudflare API credentials
CLOUDFLARE_API_TOKEN = 'c73eRoRduw8NEWr2Q7DYCNhejpHZFUHRC1yLrMJE'
CLOUDFLARE_EMAIL = 'drakipul1016@gmail.com'
CLOUDFLARE_ZONE_ID = 'c73eRoRduw8NEWr2Q7DYCNhejpHZFUHRC1yLrMJE'

# Telegram bot token
TELEGRAM_BOT_TOKEN = '7270252127:AAHXq6ZTeisM-bi9s6-n3fELQKJhrfz7C8E'

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Telegram Bot and Web Server!"

# Telegram bot functions
def start(update: Update, context: CallbackContext) -> None:
    user_first_name = update.message.from_user.first_name
    welcome_message = (
        f'👋 Halo, {user_first_name}! Selamat Datang Di Bot Vilmei.\n\n'
        'Berikut adalah perintah yang tersedia:\n\n'
        '- /payment : comming soon.\n'
        '- /listwhm : comming soon.\n'
        '- /domain : List Subdomain\n\n'
        'Channel : t.me/vilmeijugaa\n'
        'Contact : t.me/vilmeijugaa'
    )
    update.message.reply_text(welcome_message)

def list_domains(update: Update, context: CallbackContext) -> None:
    headers = {
        'Authorization': f'Bearer {CLOUDFLARE_API_TOKEN}',
        'Content-Type': 'application/json',
    }

    response = requests.get('https://api.cloudflare.com/client/v4/zones', headers=headers)
    domains = response.json().get('result', [])

    buttons = [
        [InlineKeyboardButton(domain['name'], callback_data=domain['id'])]
        for domain in domains
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Please choose a domain:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    context.user_data['zone_id'] = query.data
    query.edit_message_text(text="Masukkan nama subdomain:")

def handle_text(update: Update, context: CallbackContext) -> None:
    if 'zone_id' not in context.user_data:
        update.message.reply_text('Please select a domain first using /domain.')
        return

    if 'subdomain' not in context.user_data:
        context.user_data['subdomain'] = update.message.text
        update.message.reply_text('Masukkan IP server:')
    else:
        subdomain = context.user_data['subdomain']
        ip_address = update.message.text
        zone_id = context.user_data['zone_id']

        headers = {
            'Authorization': f'Bearer {CLOUDFLARE_API_TOKEN}',
            'Content-Type': 'application/json',
        }

        data = {
            'type': 'A',
            'name': subdomain,
            'content': ip_address,
            'ttl': 1,
            'proxied': False
        }

        response = requests.post(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records', headers=headers, json=data)
        result = response.json()

        if response.status_code == 200 and result['success']:
            update.message.reply_text(
                f'Berhasil Create Subdomain !!!\n\n'
                f'🌐 Subdomain: {subdomain}\n📍 IP: {ip_address}\n\n'
                f'Klik <a href="http://example.com">di sini</a> untuk melihat hasilnya.', 
                parse_mode='HTML'
            )
        else:
            update.message.reply_text(f'Failed to add subdomain. Error: {result.get("errors", "Unknown error")}')

        context.user_data.pop('subdomain', None)

def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('domain', list_domains))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    # Start Flask app in a separate thread
    from threading import Thread
    Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

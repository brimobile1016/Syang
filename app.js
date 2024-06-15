const express = require('express');
const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');
const token = '7270252127:AAHXq6ZTeisM-bi9s6-n3fELQKJhrfz7C8E';
const bot = new TelegramBot(token, { polling: true });

const app = express();
const PORT = process.env.PORT || 3000;

const CLOUDFLARE_API_TOKEN = 'c73eRoRduw8NEWr2Q7DYCNhejpHZFUHRC1yLrMJE';
const CLOUDFLARE_ZONE_ID = 'c73eRoRduw8NEWr2Q7DYCNhejpHZFUHRC1yLrMJE';

bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    const userFirstName = msg.from.first_name;
    const welcomeMessage = `
    👋 Halo, ${userFirstName}! Selamat Datang Di Bot Vilmei.

    Berikut adalah perintah yang tersedia:

    - /payment : coming soon.
    - /listwhm : coming soon.
    - /domain : List Subdomain

    Channel : t.me/vilmeijugaa
    Contact : t.me/vilmeijugaa
    `;
    bot.sendMessage(chatId, welcomeMessage);
});

bot.onText(/\/domain/, async (msg) => {
    const chatId = msg.chat.id;
    try {
        const response = await axios.get('https://api.cloudflare.com/client/v4/zones', {
            headers: {
                'Authorization': `Bearer ${CLOUDFLARE_API_TOKEN}`,
                'Content-Type': 'application/json'
            }
        });
        const domains = response.data.result;
        const buttons = domains.map(domain => ({
            text: domain.name,
            callback_data: domain.id
        }));
        const options = {
            reply_markup: JSON.stringify({
                inline_keyboard: buttons.map(button => [button])
            })
        };
        bot.sendMessage(chatId, 'Please choose a domain:', options);
    } catch (error) {
        console.error(error);
        bot.sendMessage(chatId, 'Failed to retrieve domains.');
    }
});

bot.on('callback_query', (query) => {
    const chatId = query.message.chat.id;
    const zoneId = query.data;
    bot.sendMessage(chatId, "Masukkan nama subdomain:");
    bot.once('message', (msg) => {
        const subdomain = msg.text;
        bot.sendMessage(chatId, "Masukkan IP server:");
        bot.once('message', async (msg) => {
            const ipAddress = msg.text;
            try {
                const response = await axios.post(`https://api.cloudflare.com/client/v4/zones/${zoneId}/dns_records`, {
                    type: 'A',
                    name: subdomain,
                    content: ipAddress,
                    ttl: 1,
                    proxied: false
                }, {
                    headers: {
                        'Authorization': `Bearer ${CLOUDFLARE_API_TOKEN}`,
                        'Content-Type': 'application/json'
                    }
                });
                if (response.data.success) {
                    bot.sendMessage(chatId, `Berhasil Create Subdomain !!!\n\n🌐 Subdomain: ${subdomain}\n📍 IP: ${ipAddress}`);
                } else {
                    bot.sendMessage(chatId, `Failed to add subdomain. Error: ${response.data.errors}`);
                }
            } catch (error) {
                console.error(error);
                bot.sendMessage(chatId, 'Failed to create DNS record.');
            }
        });
    });
});

// Express server setup
app.get('/', (req, res) => {
    res.send('Hello, this is the web interface for the Telegram bot.');
});

app.listen(PORT, () => {
    console.log(`Web server is running on port ${PORT}`);
});

console.log('Bot is running...');

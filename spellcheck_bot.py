import discord
from discord.ext import commands
import languagetool_python
from langdetect import detect

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Mapowanie języków wykrytych → kod języka w LanguageTool
LANG_MAP = {
    'pl': 'pl-PL',
    'en': 'en-US',
    'de': 'de-DE',
    'fr': 'fr-FR',
    # dodaj więcej w razie potrzeby
}

@bot.event
async def on_ready():
    print(f'✅ Bot uruchomiony jako {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignoruj boty

    tekst = message.content

    try:
        język_wykryty = detect(tekst)
        kod = LANG_MAP.get(język_wykryty, 'en-US')
        tool = languagetool_python.LanguageTool(kod)

        matches = tool.check(tekst)
        if not matches:
            return  # Brak błędów

        poprawki = []
        poprawiony_tekst = list(tekst)
        przesuniecie = 0

        for m in matches[:5]:
            start = m.offset + przesuniecie
            end = start + m.errorLength
            słowo = tekst[m.offset:m.offset + m.errorLength]
            sugestie = ', '.join(m.replacements[:2])

            # Podświetl słowo w oryginalnym tekście
            poprawiony_tekst[start:end] = list(f"**{słowo}**")
            przesuniecie += 4  # Dodaj długość '**' * 2

            poprawki.append(f"❌ **{słowo}** → 💡 {sugestie}")

        finalny_tekst = ''.join(poprawiony_tekst)
        wynik = "\n".join(poprawki)
        await message.reply(f"🔎 Wykryto błędy:
{wynik}

📝 Twoja wiadomość z podświetleniem:
{finalny_tekst}")

    except Exception as e:
        print("Błąd:", e)

import os
bot.run(os.getenv("TOKEN"))

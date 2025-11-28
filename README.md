# Live Chat Project

Django asosidagi **real-time** chat ilovasi fayl saqlash imkoniyati bilan.

## Xususiyatlar
- ✅ **Real-time messaging** - WebSocket orqali zudlik bilan xabar almashish
- ✅ **Typing indicator** - kimdir yozayotganini ko'rish
- ✅ **Online status** - user join/leave notifications
- ✅ **Har qanday fayl yuklash** - 100MB gacha, **BARCHA fayl turlari** (.exe, .bat, .sh, va h.k.)
- ✅ **Upload progress** - Yuklash jarayonini real-time kuzatish (KB)
- ✅ **Yopiq registratsiya** - faqat admin foydalanuvchi yarata oladi
- ✅ **Chat xonalari** - ko'p foydalanuvchi bilan guruh chat
- ✅ **Responsive design** - Telegram-style interfeys
- ✅ **Admin panel** - to'liq foydalanuvchi va xona boshqaruvi
- ✅ **Hech qanday fayl cheklovi yo'q** - ixtiyoriy fayl turi

## O'rnatish

1. Virtual environment yarating:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki Windows uchun: venv\Scripts\activate
```

2. Dependencies o'rnating:
```bash
pip install -r requirements.txt
```

3. Redis server ishga tushiring (production uchun):
```bash
# Linux/Mac
sudo systemctl start redis-server

# Windows (Redis yoki InMemory ishlatish)
# Development uchun Redis shart emas - InMemoryChannelLayer ishlaydi
```

4. Migration bajaring:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Superuser yarating:
6. Serverni ishga tushiring:
```bash
# Development (InMemoryChannelLayer)
python manage.py runserver

# Production (Redis + Daphne/Uvicorn)
daphne -b 0.0.0.0 -p 8000 asosiy.asgi:application
```
6. Serverni ishga tushiring:
```bash
python manage.py runserver
```

## Foydalanish

### Admin uchun:
1. Admin panel: http://127.0.0.1:8000/admin
2. Yangi foydalanuvchilar yarating
3. Chat xonalari va xabarlarni boshqaring

### Foydalanuvchilar uchun:
1. Asosiy sahifa: http://127.0.0.1:8000
## Texnologiyalar
- **Backend:** Django 4.2.7, Django Channels 4.0+
- **Real-time:** WebSocket + Redis (production) / InMemoryChannelLayer (dev)
- **Frontend:** Bootstrap 5, Vanilla JavaScript, WebSocket API
- **Ma'lumotlar bazasi:** SQLite (production uchun PostgreSQL tavsiya)
- **ASGI Server:** Daphne / Uvicorn
- **Backend:** Django 4.2.7, Django Channels, Redis
- **Frontend:** Bootstrap 5, JavaScript, WebSocket
- **Ma'lumotlar bazasi:** SQLite
- **Real-time:** Django Channels + Redis

## Registratsiya
⚠️ **Registratsiya yopiq** - yangi foydalanuvchilarni faqat admin yarata oladi.
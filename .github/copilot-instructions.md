# Live Chat - AI Kodlash Yo'riqnomasi

## Loyiha Arxitekturasi

**Bu Django real-time chat ilovasi** Telegram-ga o'xshash interfeysda. Asosiy komponentlar:

- **Backend:** Django 4.2.7 + Django Channels (WebSocket orqali real-time)
- **Database:** SQLite (`db.sqlite3`)
- **Frontend:** Bootstrap 5, Vanilla JavaScript
- **Real-time:** Django Channels + InMemoryChannelLayer (production uchun Redis tavsiya etiladi)
- **Media:** Fayllar `media/chat_files/` ga yuklanadi

### Asosiy Modullar

```
asosiy/          # Django project papkasi (settings, urls, asgi)
chat/            # Asosiy app - barcha chat funktsiyalari
  models.py      # Room, Message, RoomMember modellari
  views.py       # HTTP view'lar (login, room, file upload)
  admin.py       # Django admin customizations
  templatetags/  # Custom template filter'lar (@mention, format)
  management/    # Custom commands (create_admin)
templates/chat/  # Telegram-style HTML templatelar
media/           # Yuklangan fayllar (gitignore)
static/          # CSS, JS, images
```

## Ma'lumotlar Modeli

### Room
- **name:** Xona nomi
- **created_by:** Xona yaratuvchisi (ForeignKey -> User)
- **members:** Ko'pga-ko'p aloqa (ManyToMany through RoomMember)

### Message
- **room, user:** Xabar qayerga, kimdan
- **reply_to:** Self-ForeignKey (javob xabarlari uchun)
- **content:** Matn xabar (nullable)
- **message_type:** 'text', 'image', 'file'
- **file:** FileField (`chat_files/` ga yuklanadi)
- **file_size, file_type:** Fayl metadata (bytes, MIME type)

### RoomMember
- **room + user:** Unique together (bir user xonada faqat bir marta)
- **is_admin:** Xona admin huquqlari
- **joined_at:** Qo'shilish vaqti

## Xavfsizlik va Fayl Yuklash

### Fayl Cheklovlari (`views.py:room`)
```python
max_size = 100 * 1024 * 1024  # 100MB limit
# HECH QANDAY FAYL TURI CHEKLOVI YO'Q
```

**BARCHA fayl turlariga to'liq ruxsat** - .exe, .bat, .sh, .dll va boshqa hamma fayllar yuklanadi.

**Upload Progress:** Real-time yuklash ko'rsatkichi - KB formatda progress bar.

### Yuklash Xavfsizligi (`views.py:download_file`)
- Faqat xona a'zolari va xabar egasi yuklay oladi
- Response header'larda: `X-Content-Type-Options: nosniff`, `Content-Security-Policy: sandbox`
- Filename URL-encoded (`quote()` ishlatiladi)

## Asosiy Konventsiyalar

### Authentication
- **Yopiq registratsiya:** Faqat admin yangi userlar yarata oladi (`python manage.py create_admin`)
- Login: `/login/`, Logout: `/logout/`
- `@login_required` decorator barcha view'larda

### URL Patterns
```python
/                          # Barcha xonalar ro'yxati
/room/<id>/                # Xona chat view
/create/                   # Yangi xona yaratish
/delete-content/<id>/<type>/  # Xabar yoki fayl o'chirish (text/file/all)
/download/<id>/            # Xavfsiz fayl yuklash
```

### Template Tags (`chat_tags.py`)
- `@mention` highlight: `@username` -> rangli badge
- Format: `**bold**`, `*italic*`, `` `code` ``, URLs auto-link

### Admin Customization
- Custom UserAdmin: `room_count` qo'shilgan
- Room members count display
- Message preview (first 50 chars yoki file icon)

## Developer Workflows

### Ilk Setup
```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py create_admin --username=admin --password=admin123
python manage.py runserver
```

### Migration'lar
```bash
python manage.py makemigrations chat
python manage.py migrate
```

### Production Deploy (`deploy.sh`)
```bash
./deploy.sh  # Auto: install deps, migrate, collectstatic, create admin
```

### Static Files
- Development: `DEBUG=True` holatida `STATICFILES_DIRS` ishlatiladi
- Production: `python manage.py collectstatic` → `staticfiles/`

## Settings Muhim Qismlar (`asosiy/settings.py`)

### Production vs Development
```python
DEBUG = False  # Production
DOMEN = 'file.kspi.uz'
ALLOWED_HOSTS = ['.kokanddeveloper.uz', DOMEN, 'localhost', '*']
CSRF_TRUSTED_ORIGINS = [f'https://{DOMEN}', ...]
```

### Channels Configuration
```python
ASGI_APPLICATION = 'asosiy.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',  # Production
        'CONFIG': {"hosts": [('127.0.0.1', 6379)]},
    }
}

# Development: InMemoryChannelLayer (DEBUG=True)
```

### Locale
```python
LANGUAGE_CODE = 'uz-uz'
TIME_ZONE = 'Asia/Tashkent'
```

## Real-time (WebSocket) Implementatsiyasi

✅ **WebSocket to'liq sozlangan:**
- `chat/consumers.py` - ChatConsumer (async) real-time xabar almashish
- `chat/routing.py` - WebSocket URL routing
- `telegram_room.html` - Frontend WebSocket client integration

**Funktsiyalar:**
- Real-time xabar yuborish va qabul qilish
- Typing indicator (kimdir yozmoqda...)
- User join/leave notification
- Xabar o'chirish real-time synci
- Auto-reconnect (5 marta qayta urinish)
- Fallback HTTP POST (WebSocket ishlamasa)

**WebSocket URL Pattern:**
```
ws://localhost:8000/ws/chat/<room_id>/
```

## Kengaytirishlar uchun Tavsiyalar

1. **Online status:** Redis orqali user presence tracking
2. **Notification system:** Yangi xabarlar haqida bildirishnomalar (browser notifications)
3. **File thumbnails:** Image preview uchun `Pillow` (allaqachon requirements.txt da)
4. **Search functionality:** Xabarlarni qidirish
5. **Message reactions:** Emoji reactions (👍, ❤️, etc.)equirements.txt da)
4. **Online status:** Redis orqali user presence tracking
5. **Notification system:** Yangi xabarlar haqida bildirishnomalar

## Xato Tuzatish

### Session Issues
- `SESSION_SAVE_EVERY_REQUEST = True` - session har requestda yangilanadi
- `SESSION_EXPIRE_AT_BROWSER_CLOSE = False` - 24 soat

### File Upload 404
- `MEDIA_ROOT` to'g'ri sozlanganligini tekshiring
- `media/chat_files/` papka mavjudligini va write permission borligini tasdiqlang

### WebSocket Connection Failed
- Redis server ishga tushganligini tekshiring (production)
- `CHANNEL_LAYERS` konfiguratsiyasini ko'ring
- `asgi.py` to'g'ri sozlanganligini tasdiqlang

## Namuna Kodlar

### Yangi Xabar Yaratish
```python
message = Message.objects.create(
    room=room,
    user=request.user,
    content="Salom!",
    message_type='text'
)
```

### Fayl bilan Xabar
```python
Message.objects.create(
    room=room,
    user=request.user,
    file=uploaded_file,
    file_size=uploaded_file.size,
    file_type=content_type,
    message_type='file'
)
```

### Xona A'zolarini Olish
```python
members = room.members.all()  # ManyToMany
# yoki through model orqali:
room_members = RoomMember.objects.filter(room=room).select_related('user')
```

---

**Eslatma:** Kod o'zbek tilida comment'larga ega. Template'lar ham o'zbek tilida.

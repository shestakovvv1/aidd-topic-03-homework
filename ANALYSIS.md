# ANALYSIS.md — Investing Demo

## 1. Назначение

Веб-приложение **Investing Demo** — демо-сервис мониторинга акций. Пользователи просматривают список инструментов, детали с графиком котировок (данные Tinkoff Invest API), а авторизованные пользователи могут добавлять, редактировать и удалять акции. Доступен REST API для CRUD по акциям. Фоновые задачи Celery обновляют последние цены.

## 2. Технологический стек

| Компонент | Технология |
|-----------|------------|
| Язык / фреймворк | Python, Django |
| UI | Django Templates, Bootstrap 3 (django-crispy-forms), Plotly |
| API | Django REST Framework, django-filter |
| БД (исходно) | PostgreSQL (`psycopg2-binary`) |
| Очереди | Celery + Redis (брокер) |
| Рыночные данные | Tinkoff Invest API (`tinkoff-investments`) |
| Инфра | Docker Compose (PostgreSQL, Redis) |

## 3. Архитектура

```
config/          — настройки Django, WSGI/ASGI, Celery app, корневые URL
dashboard/       — домен «акции»: модели, views, forms, templates, API, Celery tasks, management commands
user/            — регистрация, вход, выход (стандартная модель User)
```

**Поток запросов (UI):** браузер → `config.urls` → `dashboard.urls` / `user.urls` → class-based views → ORM / сервисы (`market_data`, `graph`) → шаблоны.

**Поток API:** `/api/v1/shares` → DRF `ShareViewSet` → `ShareSerializer` → модель `Share`.

**Фон:** Celery Beat по расписанию вызывает `dashboard.tasks.update_last_price`, который через Tinkoff API обновляет `last_price` и `is_trend_high`.

## 4. Модель данных

### Share (`dashboard.models.Share`)

| Поле | Тип | Назначение |
|------|-----|------------|
| `figi` | CharField, unique | Идентификатор FIGI |
| `isin` | CharField | ISIN |
| `name` | CharField | Наименование компании |
| `ticker` | CharField, unique | Тикер |
| `currency` | CharField | Валюта |
| `uid` | CharField, unique | UID инструмента в Tinkoff |
| `last_price` | FloatField, nullable | Последняя известная цена |
| `is_trend_high` | BooleanField, nullable | Флаг роста цены |
| `updated_at` | DateTimeField, auto_now | Время обновления |

Связей с `User` в исходной модели нет. Аутентификация использует стандартную `django.contrib.auth.models.User` (логин = email как `username`).

---

## 5. Восстановленные функциональные требования

1. **Список акций.** Неавторизованный и авторизованный пользователь видит пагинированный список акций (тикер, название, ISIN, цена с цветовой индикацией тренда). Подтверждение: `ShareListView`, `dashboard/list.html`, `paginate_by = 100`.

2. **Детальная страница акции.** По клику на тикер открывается страница с названием, текущей ценой, временем обновления и интерактивным графиком исторических свечей (~180 дней). Подтверждение: `ShareDetailView`, `get_graph()` в `services/graph.py`, `detail.html`.

3. **CRUD акций для авторизованных.** Только аутентифицированный пользователь может создавать, редактировать и удалять акции через формы. Подтверждение: `ShareCreateView` / `UpdateView` / `DeleteView` + `IsUserAuthenticatedMixin`, `ShareModelForm`.

4. **Регистрация.** Пользователь регистрируется по email и паролю (с подтверждением); при успехе выполняется вход и редирект на главную. Подтверждение: `RegistrationView`, `RegistrationForm.save()` → `User.objects.create_user(email, email, password)`.

5. **Авторизация и выход.** Вход по email/паролю; при ошибке показывается сообщение; выход через `logout` с редиректом на главную. Подтверждение: `AuthView`, `LogoutView`, шаблоны `user/auth.html`, `user/registration.html`.

6. **REST API акций.** Endpoint `/api/v1/shares` предоставляет ModelViewSet (CRUD) с пагинацией, фильтрацией по `name`/`ticker`, поиском и сортировкой. Подтверждение: `ShareViewSet`, `ShareSerializer`, `REST_FRAMEWORK` в `settings.py`.

7. **Загрузка справочника акций.** Management-команда `add_shares` загружает инструменты из Tinkoff Invest API в БД (`get_or_create` по полям акции). Подтверждение: `dashboard/management/commands/add_shares.py`.

8. **Периодическое обновление цен.** Celery-задача `update_last_price` для каждой акции запрашивает последнюю цену, обновляет `last_price` и выставляет `is_trend_high`. Подтверждение: `dashboard/tasks.py`, `config/celery.py` (`beat_schedule`).

9. **Админка.** Модель `Share` зарегистрирована в Django Admin с поиском и отображением ключевых полей. Подтверждение: `dashboard/admin.py`.

---

## 6. Дефекты и неоднозначности

### Критические / блокирующие запуск

1. **Пустой `SECRET_KEY`** в `config/settings.py` — Django не стартует корректно в проде и может падать на ряде операций.
2. **Пустой `ALLOWED_HOSTS`** при потенциальном `DEBUG=False` блокирует доступ; даже для локальной разработки лучше явно указать hosts.
3. **Жёсткая зависимость от PostgreSQL** без локального SQLite — без Docker/Postgres проект не поднимается.
4. **`CELERY_BROKER_URL` на Redis** — при импорте Celery/`config.__init__` приложение чувствительно к отсутствию Redis/Docker.
5. **Пустой `TINKOFF_TOKEN`** — детальная страница и команда `add_shares` падают при обращении к API.

### Ошибки реализации

6. **URL пользователей:** `path("user", include(...))` без слэша → маршруты вида `/userlogin/` вместо `/user/login/` (`config/urls.py`).
7. **`IsUserAuthenticatedMixin.handle_no_permission`** объявлен как `@staticmethod` и редиректит на `dashboard:index` вместо страницы входа — некорректное поведение для неавторизованных.
8. **`AuthView.post`** не вызывает `form.is_valid()` и читает `form.data` напрямую.
9. **`RegistrationForm.clean`** обращается к `cleaned_data["email"]` без защиты от KeyError при невалидном email.
10. **`ShareDeleteView` docstring** говорит «Удаление задачи» — копипаста.
11. **Сравнение цен в `update_last_price`:** при `last_price is None` сравнение ловится общим `except`; дробная часть цены Tinkoff (`nano`) игнорируется — используется только `units`.
12. **`add_shares`:** `get_or_create` со всеми полями в kwargs (не только lookup) может создавать дубликаты при изменении метаданных или падать на unique constraints непредсказуемо.

### Неоднозначности

13. Email используется как `username` стандартной модели User — отдельной кастомной user-модели нет; поле `User.email` может не совпадать с ожиданиями уникальности email в Django по умолчанию.
14. Расписание Celery Beat в коде: комментарий «every-5-min», фактически `schedule: 10.0` (секунды).
15. API не требует аутентификации — полный CRUD акций доступен анонимно через REST, тогда как UI CRUD закрыт mixin’ом.
16. Зависимости сильно устарели (Django 4.1.7 и др.); пакет `tinkoff-investments` — beta.
17. Цвет ячейки цены при `is_trend_high is None` всё равно попадает в ветку «падение» (шаблон).

# Анализ Django-проекта "Investing"

## Назначение проекта
Веб-приложение для мониторинга и анализа акций с использованием данных Tinkoff Invest API. Позволяет пользователям отслеживать акции, просматривать графики цен и получать обновления через фоновые задачи.

## Технологический стек
- **Backend**: Django 4.1.7
- **Database**: PostgreSQL (требуется переключение на SQLite для локальной разработки)
- **Task Queue**: Celery 5.2.7 с Redis 4.5.1
- **API**: Django REST Framework 3.14.0
- **Frontend**: Bootstrap 3, Plotly 5.13.1 для графиков
- **External API**: Tinkoff Invest API (tinkoff-investments 0.2.0b50)
- **Forms**: django-crispy-forms 2.0 с crispy-bootstrap3
- **Development**: black, isort, mypy-extensions

## Архитектура
Проект состоит из трёх Django-приложений:

### 1. config
- Глобальные настройки проекта
- Конфигурация Celery
- URL-маршрутизация

### 2. dashboard
- **Модели**: Share (акции с полями figi, isin, name, ticker, currency, uid, last_price, is_trend_high, updated_at)
- **Views**: CRUD для акций (ShareListView, ShareDetailView, ShareCreateView, ShareUpdateView, ShareDeleteView)
- **Services**:
  - market_data.py: получение последних цен из Tinkoff API
  - graph.py: генерация графиков цен за 180 дней
- **Tasks**: Celery-задача update_last_price() для обновления цен каждые 10 секунд
- **API**: REST API v1 для работы с акциями
- **Management Commands**: команда add_shares для первоначальной загрузки акций

### 3. user
- **Модели**: использует стандартную модель User Django
- **Views**: AuthView (авторизация), RegistrationView (регистрация), LogoutView (выход)
- **Forms**: AuthForm, RegistrationForm

## Функциональные требования (восстановленные из кода)

1. **Аутентификация и авторизация**
   - Регистрация новых пользователей (подтверждено в user/views.py: RegistrationView)
   - Вход в систему по email и паролю (подтверждено в user/views.py: AuthView)
   - Выход из системы (подтверждено в user/views.py: LogoutView)
   - Защита CRUD-операций для авторизованных пользователей (подтверждено в dashboard/views.py: IsUserAuthenticatedMixin)

2. **Управление акциями**
   - Просмотр списка всех акций с пагинацией (подтверждено в dashboard/views.py: ShareListView)
   - Просмотр детальной информации об акции с графиком цен (подтверждено в dashboard/views.py: ShareDetailView, services/graph.py)
   - Добавление новых акций (подтверждено в dashboard/views.py: ShareCreateView)
   - Редактирование данных акций (подтверждено в dashboard/views.py: ShareUpdateView)
   - Удаление акций (подтверждено в dashboard/views.py: ShareDeleteView)

3. **Мониторинг цен**
   - Автоматическое обновление цен акций через Celery-задачи (подтверждено в dashboard/tasks.py: update_last_price)
   - Отображение тренда цены (растёт/падает) с цветовой индикацией (подтверждено в dashboard/models.py: is_trend_high, templates/dashboard/list.html)
   - Получение данных из Tinkoff Invest API (подтверждено в dashboard/services/market_data.py)

4. **REST API**
   - API endpoint /api/v1/shares для работы с акциями (подтверждено в dashboard/api/urls.py)

5. **Администрирование**
   - Django Admin для управления акциями (подтверждено в dashboard/admin.py)

## Найденные дефекты и неоднозначности

### Критические дефекты
1. **Пустой SECRET_KEY** в config/settings.py (строка 6) - приложение не запустится без валидного ключа
2. **Пустой ALLOWED_HOSTS** в config/settings.py (строка 10) - проблемы с доступом к приложению
3. **Настроена PostgreSQL** вместо SQLite для локальной разработки (строки 96-103) - требует Docker/PostgreSQL
4. **Настроен Celery с Redis** (строка 141) - приложение может падать при запуске без Redis
5. **Пустой TINKOFF_TOKEN** в config/settings.py (строка 134) - API не будет работать

### Логические ошибки
6. **Неверная логика определения тренда** в dashboard/tasks.py (строки 16-19):
   ```python
   if share.last_price > last_price:
       is_trend_high = False
   else:
       is_trend_high = True
   ```
   Если текущая цена больше новой цены, тренд считается высоким (True), что нелогично. Должно быть наоборот.

### Неоднозначности
7. **Отсутствие валидации** уникальности полей в формах (dashboard/forms.py не проверен полностью)
8. **Отсутствие обработки ошибок** при вызове Tinkoff API в services/graph.py
9. **Интервал обновления цен** установлен на 10 секунд (config/celery.py:16) - может быть слишком часто для production
10. **Отсутствие миграций** для новых моделей в будущем

### Потенциальные проблемы
11. **Устаревшие зависимости** в requirements.txt (Django 4.1.7, Celery 5.2.7 и др.)
12. **Использование deprecated библиотек** (Bootstrap 3, старые версии Plotly)
13. **Отсутствие тестов** для критической бизнес-логики (tests.py существует, но не проверен)
14. **Жёстко закодированные параметры** (интервал графиков 180 дней в graph.py:16)

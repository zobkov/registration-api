Searched codebase for "сделай краткое ТЗ для реализации API для обработки ргеистраций. Уже существующая БД постгреса туда надо будет api обрабатывать ", 25 results

Краткое ТЗ: API для обработки регистраций форума (PostgreSQL)
+ FastAPI
+ Alembic
+ SQLAlchemy
use .env for db auth

1. Цель  
Создать backend API, который принимает данные с формы регистрации, валидирует их и сохраняет в уже существующую PostgreSQL БД.

1. Область работ  
- Прием регистраций из веб-формы.  
- Валидация и нормализация данных.  
- Запись в PostgreSQL.  
- Базовая защита от спама/дубликатов.  
- Возврат понятного статуса клиенту.

1. Формат данных регистрации  
Общие поля:  
- fullName: string  
- status: enum (speaker | participant | guest)  
- transport: enum (Личный транспорт | Общественный транспорт | Спец. развозка от КБК | Онлайн)  
- carNumber: string | null (обязательно только при transport=Личный транспорт)  
- passport: string (объединенное поле серия+номер)

Поля для participant:  
- adult18: enum (Да | Нет)  
- region: string  
- participantStatus: enum (Среднее образование | Высшее образование | Работаю)  
- email: string  
- track: enum (8 треков)

Поля для speaker/guest:  
- email: string

4. API контракт  
POST /api/v1/registrations  
- Content-Type: application/json  
- Body: по структуре выше  
- Успех: 201  
  - { id, status: "created", createdAt }  
- Ошибка валидации: 400  
  - { status: "validation_error", errors: [...] }  
- Дубликат (например, по email+passport): 409  
- Ошибка сервера: 500

GET /api/v1/registrations/:id (опционально, для админки)  
- Возвращает карточку регистрации.

5. Правила валидации  
- fullName, status, transport, passport, email обязательны.  
- participant-поля обязательны только для status=participant.  
- carNumber обязателен только при Личный транспорт.  
- Если transport=Онлайн, carNumber должен быть null.  
- Проверка формата email.  
- Ограничения длины строк (защита от мусорных данных).

6. Требования к БД  
- Использовать существующую PostgreSQL.  
- Таблица site_registrations (или адаптация к текущей схеме):  
  - id (uuid/bigserial, PK)  
  - full_name  
  - status  
  - email  
  - adult18 (nullable)  
  - region (nullable)  
  - participant_status (nullable)  
  - track (nullable)  
  - transport  
  - car_number (nullable)  
  - passport  
  - created_at  
- Индексы: created_at, status, email.  
- Уникальность: по согласованному правилу (например email+passport+status).

7. Безопасность  
- Только параметризованные SQL-запросы/ORM (без SQL-инъекций).  
- Rate limit на endpoint регистрации.  
- Логирование ошибок без утечки персональных данных.  
- CORS только для домена сайта.

8. Нефункциональные требования  
- Время ответа POST < 500ms при нормальной нагрузке.  
- JSON API, UTF-8.  
- Подготовка к масштабированию (версионирование /v1).

9. Критерии приемки  
- Все 3 сценария (speaker/participant/guest) корректно сохраняются в БД.  
- Невалидные данные отклоняются с понятными ошибками.  
- carNumber логика работает по transport.  
- Нет дублей по согласованному правилу.  
- Есть smoke-тесты и минимум 1 интеграционный тест с PostgreSQL.

Если нужно, следующим шагом могу дать такой же краткий документ уже в формате “готово к задаче в Jira” (с Definition of Done и чеклистом тестирования).
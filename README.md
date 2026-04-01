# Запуск сервиса:
## Локально
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

## Или Docker
docker compose up --build


# API документация
Swagger UI - http://localhost:8000/docs

# Эндпойнты
Метод POST - путь /users - создать пользователя
Метод GET - путь /users - получить всех пользователей
Метод POST - путь /users/lock - заблокировать пользователя
Метод POST - путь /users/free - разблокировать пользователя
Метод GET - путь /health - проверка состояния работы сервиса

# Тесты
## Запуск
python -m pytest tests/test_api.py -v

## Покрытие
coverage run -m pytest tests/ && coverage report
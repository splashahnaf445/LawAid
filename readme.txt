-- setup commands for terminals

mkdir lawaid && cd lawaid && mkdir backend db

cd backend

python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate

pip install "django>=5.2,<5.3" djangorestframework djangorestframework-simplejwt \
            django-cors-headers "psycopg[binary]" python-dotenv

pip freeze > requirements.txt

django-admin startproject config .

python manage.py startapp accounts

init:
	pipenv run python manage.py migrate
	pipenv run python manage.py create_default_superuser --user admin --password admin || \
	    echo "--------------------------------------------------------------------"; \
	    echo "- Everything is OK -- Use admin:admin credentials in Django admin! -"; \
	    echo "--------------------------------------------------------------------"
	pipenv run python manage.py runserver 0.0.0.0:8000

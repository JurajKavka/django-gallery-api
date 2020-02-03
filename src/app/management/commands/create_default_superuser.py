import logging
from django.contrib.auth import get_user_model
from django.core import exceptions
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS
from django.utils.text import capfirst


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Created default super user.
    """
    help = 'Create superuser with password.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UserModel = get_user_model()
        self.username_field = self.UserModel._meta.get_field(self.UserModel.USERNAME_FIELD)

    def add_arguments(self, parser):
        parser.add_argument('--username', nargs='?', type=str, required=True,
                            help='Username')

        parser.add_argument('--password', nargs='?', type=str, required=True,
                            help='Password')

        parser.add_argument('--database', default=DEFAULT_DB_ALIAS,
                            help='Specifies the database to use. Default is "default".')

    def handle(self, *args, **options):
        username = options[self.UserModel.USERNAME_FIELD]
        database = options['database']
        verbose_field_name = self.username_field.verbose_name
        password = options['password']

        user_data = {}

        # validate username
        error_msg = self._validate_username(username, verbose_field_name, database)
        if error_msg:
            raise CommandError(error_msg)

        # init minimal user data
        user_data[self.UserModel.USERNAME_FIELD] = username

        # create superuser
        new_user = (self.UserModel._default_manager.db_manager(database)
                    .create_superuser(**user_data))

        # set password
        new_user.set_password(password)
        new_user.save()

    def _validate_username(self, username, verbose_field_name, database):
        """Validate username. If invalid, return a string error message."""
        if self.username_field.unique:
            try:
                self.UserModel._default_manager.db_manager(database).get_by_natural_key(username)
            except self.UserModel.DoesNotExist:
                pass
            else:
                return 'Error: That %s is already taken.' % verbose_field_name
        if not username:
            return '%s cannot be blank.' % capfirst(verbose_field_name)
        try:
            self.username_field.clean(username, None)
        except exceptions.ValidationError as e:
            return '; '.join(e.messages)

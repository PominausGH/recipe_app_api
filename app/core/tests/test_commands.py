"""
"""


from unittest.mock import patch

from pyscopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.mangement.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands
    """
    
    def test_wait_for_db(self, patched_check):
        """ Test waiting for database to be ready."""

        patched_check.return_value = True

        call_command('Wait_for_db')

        patched_check.assert_called_once_with(database=['default'])


    def test_wait_for_db_delay(self, patched_check):

        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]
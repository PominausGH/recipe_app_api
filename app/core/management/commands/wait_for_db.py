""" 
django commnad to wait for db
"""
import time

from psycopg2 import OperationalError as Psycopg2opError

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """ django command to wait for db"""

    def handle(self, *args, **commands):
        """ entry point for command"""
        self.stdout.write('waiting for database')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2opError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 seconds...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('database avaialable!'))
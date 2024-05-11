""" 
django commnad to wait for db
"""
import time

from psycopg2 import OperationalError as Psycopg2opError
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """ django command to wait for db"""

    def handle(self, *args, **commands):
        """ entry point for command"""
        self.stdout.write('waiting for database')
        # db_up = False
        db_conn = None
        while not db_conn:
            try:
                # self.check(databases=['default'])
                db_conn = connections['default']
                db_up = True
            except (Psycopg2opError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 seconds...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('database avaialable!'))
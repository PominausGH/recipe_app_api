""" 
django commnad to wait for db
"""
import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """ django command to wait for db"""

    def handle(self, *args, **commands):
        """ entry point for command"""

        self.stdout.write('waiting for db')

        db_conn = None

        while db_conn is False:
            try:
                db_conn = connections['default']
                # self.check(databases=['default'])
                # db_up = True
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 seconds...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('database avaialable!'))
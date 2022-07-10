from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create Super User'


    def handle(self, *args, **options):
        try:
            User.objects.get(username="admin")
        except User.DoesNotExist:
            #move to settings.py
            User.objects.create_superuser('admin', 'attahzuzu@gmail.com', 'password')
            
            self.stdout.write(self.style.SUCCESS('Admin has been created '))
        self.stdout.write(self.style.SUCCESS('Finished processing'))
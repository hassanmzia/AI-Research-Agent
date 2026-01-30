"""Management command to create a default user for development."""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create a default admin user for development"

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@research.local",
                password="admin123",
                first_name="Admin",
                last_name="User",
            )
            self.stdout.write(self.style.SUCCESS("Created default admin user (admin/admin123)"))
        else:
            self.stdout.write(self.style.WARNING("Default admin user already exists"))

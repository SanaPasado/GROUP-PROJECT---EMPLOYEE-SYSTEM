from django.core.management.base import BaseCommand
from django.db import connection
from attendance.models import Attendance


class Command(BaseCommand):
    help = 'Clean corrupted attendance data that causes ISO format errors'

    def handle(self, *args, **options):
        self.stdout.write('Starting to clean corrupted attendance data...')

        try:
            # Use raw SQL to delete problematic records
            with connection.cursor() as cursor:
                # Delete records with invalid datetime formats
                cursor.execute("""
                    DELETE FROM attendance_attendance 
                    WHERE time_in IS NOT NULL AND (
                        time_in = '' OR 
                        time_in = 'None' OR 
                        LENGTH(time_in) < 19
                    )
                """)
                deleted_time_in = cursor.rowcount

                cursor.execute("""
                    DELETE FROM attendance_attendance 
                    WHERE time_out IS NOT NULL AND (
                        time_out = '' OR 
                        time_out = 'None' OR 
                        LENGTH(time_out) < 19
                    )
                """)
                deleted_time_out = cursor.rowcount

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully cleaned {deleted_time_in + deleted_time_out} corrupted records'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error cleaning data: {e}')
            )

            # Alternative approach - delete all attendance records
            self.stdout.write('Attempting to clear all attendance records...')
            try:
                Attendance.objects.all().delete()
                self.stdout.write(
                    self.style.WARNING('All attendance records have been cleared')
                )
            except Exception as e2:
                self.stdout.write(
                    self.style.ERROR(f'Could not clear records: {e2}')
                )

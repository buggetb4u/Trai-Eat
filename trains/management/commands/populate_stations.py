from django.core.management.base import BaseCommand
from trains.models import Station

class Command(BaseCommand):
    help = 'Populates the database with train stations'

    def handle(self, *args, **kwargs):
        stations = [
            # Bhopal & Surrounding
            {'name': 'Bhopal Junction', 'code': 'BPL', 'city': 'Bhopal', 'state': 'Madhya Pradesh'},
            {'name': 'Habibganj / Rani Kamlapati', 'code': 'RKMP', 'city': 'Bhopal', 'state': 'Madhya Pradesh'},
            {'name': 'Itarsi Junction', 'code': 'ET', 'city': 'Itarsi', 'state': 'Madhya Pradesh'},
            {'name': 'Hoshangabad', 'code': 'HBD', 'city': 'Hoshangabad', 'state': 'Madhya Pradesh'},
            {'name': 'Sehore', 'code': 'SEH', 'city': 'Sehore', 'state': 'Madhya Pradesh'},
            {'name': 'Obedullaganj', 'code': 'ODG', 'city': 'Obedullaganj', 'state': 'Madhya Pradesh'},
            {'name': 'Bairagarh', 'code': 'BIH', 'city': 'Bhopal', 'state': 'Madhya Pradesh'},
        ]

        for station_data in stations:
            station, created = Station.objects.get_or_create(
                code=station_data['code'],
                defaults={
                    'name': station_data['name'],
                    'city': station_data['city'],
                    'state': station_data['state']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created station {station.name}'))
            else:
                self.stdout.write(f'Station {station.name} already exists') 
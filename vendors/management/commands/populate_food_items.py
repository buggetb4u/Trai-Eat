from django.core.management.base import BaseCommand
from vendors.models import Vendor, FoodCategory, FoodItem
from trains.models import Station, Platform

class Command(BaseCommand):
    help = 'Populates the database with initial food items and a default vendor'

    def handle(self, *args, **kwargs):
        # Create a default station and platform if they don't exist
        station, _ = Station.objects.get_or_create(
            code='CST',
            defaults={
                'name': 'Central Station',
                'city': 'Mumbai',
                'state': 'Maharashtra'
            }
        )
        
        platform, _ = Platform.objects.get_or_create(
            station=station,
            number='1'
        )

        # Create a default vendor
        vendor, created = Vendor.objects.get_or_create(
            name='Train Food Express',
            defaults={
                'owner_name': 'John Doe',
                'phone_number': '+919876543210',
                'email': 'trainfood@example.com',
                'station': station,
                'platform': platform,
                'description': 'Serving delicious food on your journey',
                'is_active': True
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created vendor: {vendor.name}'))
        else:
            self.stdout.write(f'Using existing vendor: {vendor.name}')

        # Create food categories
        categories = {
            'Main Course': 'Hearty main dishes',
            'Snacks': 'Quick bites and appetizers',
            'Beverages': 'Hot and cold drinks',
            'Desserts': 'Sweet treats'
        }

        for name, description in categories.items():
            category, created = FoodCategory.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

        # Create food items
        food_items = [
            {
                'name': 'Veg Biryani',
                'description': 'Fragrant basmati rice cooked with mixed vegetables and aromatic spices',
                'price': 180.00,
                'category': 'Main Course',
                'is_vegetarian': True,
                'is_available': True,
                'preparation_time': 20,
                'image': 'media/food_images/Veg_Biryani.jpg'
            },
            {
                'name': 'Chicken Biryani',
                'description': 'Tender chicken pieces cooked with basmati rice and special biryani spices',
                'price': 220.00,
                'category': 'Main Course',
                'is_vegetarian': False,
                'is_available': True,
                'preparation_time': 25,
                'image': 'media/food_images/Chicken_Biryani.jpg'
            },
            {
                'name': 'Butter Chicken',
                'description': 'Tender chicken in a rich, creamy tomato-based curry',
                'price': 250.00,
                'category': 'Main Course',
                'is_vegetarian': False,
                'is_available': True,
                'preparation_time': 20,
                'image': 'media/food_images/Butter_Chicken.jpg'
            },
            {
                'name': 'Dal Makhani',
                'description': 'Black lentils cooked overnight with butter and cream',
                'price': 180.00,
                'category': 'Main Course',
                'is_vegetarian': True,
                'is_available': True,
                'preparation_time': 15,
                'image': 'media/food_images/Dal_Makhani.jpeg'
            },
            {
                'name': 'Palak Paneer',
                'description': 'Cottage cheese cubes in a creamy spinach gravy',
                'price': 200.00,
                'category': 'Main Course',
                'is_vegetarian': True,
                'is_available': True,
                'preparation_time': 15,
                'image': 'media/food_images/Palak_Paneer.jpeg'
            },
            {
                'name': 'Naan',
                'description': 'Soft and fluffy tandoor-baked bread',
                'price': 30.00,
                'category': 'Breads',
                'is_vegetarian': True,
                'is_available': True,
                'preparation_time': 10,
                'image': 'food_images/Naan.jpg'
            },
            {
                'name': 'Masala Dosa',
                'description': 'Crispy rice crepe filled with spiced potato filling',
                'price': 120.00,
                'category': 'Breakfast',
                'is_vegetarian': True,
                'is_available': True,
                'preparation_time': 15,
                'image': 'media/food_images/Masala_Dosa.webp'
            },
            {
                'name': 'Idli Sambar',
                'description': 'Steamed rice cakes served with lentil soup',
                'price': 100.00,
                'category': 'Breakfast',
                'is_vegetarian': True,
                'is_available': True,
                'preparation_time': 10,
                'image': 'media/food_images/Idli_Sambar.jpg'
            },
            {
                'name': 'Samosa',
                'description': 'Crispy pastry filled with spiced potatoes and peas',
                'price': 40.00,
                'category': 'Snacks',
                'is_vegetarian': True,
                'is_available': True,
                'preparation_time': 10,
                'image': 'media/food_images/Samosa.jpg'
            },
            {
                'name': 'Pakora',
                'description': 'Assorted vegetables dipped in spiced gram flour batter and deep-fried',
                'price': 80.00,
                'category': 'Snacks',
                'is_vegetarian': True,
                'is_available': True,
                'preparation_time': 15,
                'image': 'media/food_images/Pakora.jpeg'
            },
            {
                'name': 'Vada',
                'description': 'Crispy fried lentil donuts',
                'price': 60.00,
                'category': 'Snacks',
                'is_vegetarian': True,
                'is_available': True,
                'preparation_time': 10,
                'image': 'media/food_images/Vada.jpg'
            },
            {
                'name': 'Gulab Jamun',
                'description': 'Soft milk solids balls soaked in sugar syrup',
                'price': 60.00,
                'category': 'Desserts',
                'is_vegetarian': True,
                'is_available': True,
                'preparation_time': 10,
                'image': 'media/food_images/Gulab_Jamun.webp'
            },
            {
                'name': 'Jalebi',
                'description': 'Crispy pretzel-shaped sweet soaked in sugar syrup',
                'price': 50.00,
                'category': 'Desserts',
                'is_vegetarian': True,
                'is_available': True,
                'preparation_time': 10,
                'image': 'media/food_images/Jalebi.webp'
            },
            {
                'name': 'Masala Chai',
                'description': 'Spiced Indian tea with milk',
                'price': 20.00,
                'category': 'Beverages',
                'is_vegetarian': True,
                'is_available': True,
                'preparation_time': 5,
                'image': 'media/food_images/Masala_Chai.jpg'
            }
        ]

        for item_data in food_items:
            category, created = FoodCategory.objects.get_or_create(name=item_data['category'])
            food_item, created = FoodItem.objects.get_or_create(
                vendor=vendor,
                name=item_data['name'],
                defaults={
                    'description': item_data['description'],
                    'price': item_data['price'],
                    'category': category,
                    'is_vegetarian': item_data['is_vegetarian'],
                    'is_available': item_data['is_available'],
                    'preparation_time': item_data['preparation_time'],
                    'image': item_data['image']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created food item: {food_item.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Food item already exists: {food_item.name}')) 
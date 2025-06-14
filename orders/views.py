from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem, PNROrder, Cart, CartItem, Station, Train
from vendors.models import FoodItem
from .forms import PNROrderForm, TrackOrderForm, CheckoutForm
from trains.models import Platform
import uuid
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

# Create your views here.

@login_required
def order_list(request):
    """View to display a list of orders for the logged-in user."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {
        'orders': orders
    })

@login_required
def order_detail(request, order_number):
    """View to display details of a specific order."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_detail.html', {
        'order': order
    })

@login_required
def cart(request):
    """View to display the user's shopping cart."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'orders/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, food_id):
    """View to add a food item to the cart."""
    food_item = get_object_or_404(FoodItem, id=food_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, food_item=food_item)

    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'{food_item.name} quantity was updated in your cart.')
    else:
        messages.success(request, f'{food_item.name} was added to your cart.')

    return redirect('vendors:food_list')

@login_required
def remove_from_cart(request, item_id):
    """View to remove an item from the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    food_name = cart_item.food_item.name
    cart_item.delete()
    messages.success(request, f'{food_name} has been removed from your cart.')
    return redirect('orders:cart')

@login_required
def update_cart(request, item_id):
    """View to update the quantity of an item in the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully!')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart!')
            
    return redirect('orders:cart')

@login_required
def add_and_checkout(request, food_id):
    """
    Adds a food item to the cart and immediately redirects to the checkout page.
    """
    food_item = get_object_or_404(FoodItem, id=food_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, food_item=food_item)

    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.info(request, f'An existing {food_item.name} is in your cart. Its quantity has been updated.')
    else:
        messages.success(request, f'{food_item.name} has been added to your cart.')

    return redirect('orders:checkout')

@login_required
def checkout(request):
    """View to handle the checkout process."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('vendors:food_list')

    if request.method == 'POST':
        order_type = request.POST.get('order_type')
        
        if order_type == 'pnr':
            # Handle PNR order
            pnr_number = request.POST.get('pnr_number')
            mobile_number = request.POST.get('mobile_number')
            delivery_station = request.POST.get('delivery_station')
            special_instructions = request.POST.get('special_instructions')
            
            # Validate required fields
            if not all([pnr_number, mobile_number, delivery_station]):
                messages.error(request, "Please fill in all required fields.")
                return redirect('orders:checkout')
            
            # Store data in session
            request.session['pnr_number'] = pnr_number
            request.session['mobile_number'] = mobile_number
            request.session['delivery_station'] = delivery_station
            request.session['special_instructions'] = special_instructions
            
        else:
            # Handle station-based order
            station_code = request.POST.get('station')
            train_name = request.POST.get('train_name')
            train_number = request.POST.get('train_number')
            class_type = request.POST.get('class_type')
            mobile_number = request.POST.get('mobile_number')
            special_instructions = request.POST.get('special_instructions')
            
            # Validate required fields
            if not all([station_code, train_name, train_number, class_type, mobile_number]):
                messages.error(request, "Please fill in all required fields.")
                return redirect('orders:checkout')
            
            # Store data in session
            request.session['station_code'] = station_code
            request.session['train_name'] = train_name
            request.session['train_number'] = train_number
            request.session['class_type'] = class_type
            request.session['mobile_number'] = mobile_number
            request.session['special_instructions'] = special_instructions

        # Create order and redirect to payment
        with transaction.atomic():
            if order_type == 'pnr':
                # Create order with PNR details
                station, created = Station.objects.get_or_create(
                    code=delivery_station,
                    defaults={'name': delivery_station}
                )
                order = Order.objects.create(
                    user=request.user,
                    delivery_station=station,
                    order_number=str(uuid.uuid4())[:8].upper(),
                    total_amount=cart.get_total(),
                    special_instructions=special_instructions,
                    delivery_time=timezone.now() + timedelta(hours=1)
                )
            else:
                # Create order with station and train details
                station, created = Station.objects.get_or_create(code=station_code, defaults={'name': station_code})
                train = Train.objects.get_or_create(
                    number=train_number,
                    defaults={
                        'name': train_name,
                        'class_type': class_type
                    }
                )[0]
                
                order = Order.objects.create(
                    user=request.user,
                    train=train,
                    delivery_station=station,
                    order_number=str(uuid.uuid4())[:8].upper(),
                    total_amount=cart.get_total(),
                    special_instructions=special_instructions,
                    delivery_time=timezone.now() + timedelta(hours=1)
                )

            # Move items from cart to order
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    food_item=cart_item.food_item,
                    quantity=cart_item.quantity,
                    price=cart_item.food_item.price
                )
            
            # Clear the cart
            cart.items.all().delete()
            
            # Store order ID in session for the payment app
            request.session['order_id'] = order.id
            
            # Redirect to the payment process
            return redirect('payment:process')

    return render(request, 'orders/checkout.html', {'cart': cart})

@login_required
def order_confirmation(request, order_number):
    """A simple order confirmation page."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Mark the order as preparing
    order.status = 'PREPARING'
    order.save()
    
    messages.success(request, f"Your order #{order.order_number} has been placed successfully!")
    return render(request, 'orders/order_confirmation.html', {'order': order})

@login_required
def track_order(request, order_number):
    """View to track an order's status."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/track_order.html', {
        'order': order
    })

@login_required
def cancel_order(request, order_number):
    """View to cancel an order."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    if order.status in ['PENDING', 'PREPARING']:
        order.status = 'CANCELLED'
        order.save()
        messages.success(request, 'Order cancelled successfully!')
    else:
        messages.error(request, 'Order cannot be cancelled.')
    return redirect('orders:order_list')

@login_required
def add_review(request, order_number):
    """View to add a review for an order."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    if request.method == 'POST':
        # TODO: Implement review functionality
        messages.success(request, 'Review added successfully!')
        return redirect('orders:order_detail', order_number=order_number)
    return render(request, 'orders/add_review.html', {
        'order': order
    })

@login_required
def pnr_order(request):
    if request.method == 'POST':
        form = PNROrderForm(request.POST)
        if form.is_valid():
            pnr_order = form.save(commit=False)
            pnr_order.user = request.user
            pnr_order.save()
            messages.success(request, 'PNR order created successfully!')
            return redirect('orders:pnr_order_list')
    else:
        form = PNROrderForm()
    return render(request, 'orders/pnr_order.html', {'form': form})

@login_required
def pnr_order_list(request):
    orders = PNROrder.objects.filter(user=request.user)
    return render(request, 'orders/pnr_order_list.html', {'orders': orders})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})

@login_required
def update_cart_item(request, item_id):
    """View to update the quantity of an item in the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully!')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart!')
            
    return redirect('orders:cart')

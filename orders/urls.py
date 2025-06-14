from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/update-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('order/<str:order_number>/', views.order_detail, name='order_detail'),
    path('pnr-order/', views.pnr_order, name='pnr_order'),
    path('pnr-orders/', views.pnr_order_list, name='pnr_order_list'),
    path('add-and-checkout/<int:food_id>/', views.add_and_checkout, name='add_and_checkout'),
    path('cancel/<str:order_number>/', views.cancel_order, name='cancel_order'),
] 
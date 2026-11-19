
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Website pages
    path('', views.home, name='home'),
    path('looks/', views.looks, name='looks'),
    path('new-in/', views.new_in, name='new_in'),
    path('studio/', views.studio, name='studio'),
    path('bag/', views.bag, name='bag'),

    # Backend API endpoints
    path('api/orders/', views.api_create_order, name='api_create_order'),
    path('api/subscribe/', views.api_subscribe, name='api_subscribe'),

    # Custom Admin Panel
    path('admin-login/', views.AdminLoginView.as_view(), name='admin_login'),
    path('admin-logout/', LogoutView.as_view(next_page='admin_login'), name='admin_logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/products/', views.admin_products, name='admin_products'),
    path('dashboard/orders/', views.admin_orders, name='admin_orders'),
    path('dashboard/orders/<int:pk>/', views.admin_order_detail, name='admin_order_detail'),
    path('dashboard/subscribers/', views.admin_subscribers, name='admin_subscribers'),
]
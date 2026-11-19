import csv
import json
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST, require_http_methods
from .models import Product, Order, OrderItem, Subscriber
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy


# --- HTML Page Views ---
def home(request):
    return render(request, 'fashion/index.html')


def looks(request):
    return render(request, 'fashion/looks.html')


def new_in(request):
    return render(request, 'fashion/new_in.html')


def studio(request):
    return render(request, 'fashion/studio.html')


def bag(request):
    return render(request, 'fashion/bags.html')


# --- Backend JSON APIs ---
@require_POST
def api_create_order(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    items = payload.get('items', [])
    if not items:
        return JsonResponse({'error': 'Your bag is empty'}, status=400)

    full_name = (payload.get('full_name') or '').strip()
    email = (payload.get('email') or '').strip()
    city = (payload.get('city') or '').strip()
    postal_code = (payload.get('postal_code') or '').strip()
    promo_code = (payload.get('promo_code') or '').strip().upper()

    if not all([full_name, email, city, postal_code]):
        return JsonResponse({'error': 'Please fill in all delivery fields'}, status=400)

    # Calculate totals securely on the server
    subtotal = sum(Decimal(str(it['price'])) * int(it['qty']) for it in items)
    discount = (subtotal * Decimal('0.10')).quantize(Decimal('0.01')) if promo_code == 'TREAD10' else Decimal('0.00')
    shipping = Decimal('12.00') if (0 < subtotal < 200) else Decimal('0.00')
    total = max(Decimal('0.00'), subtotal - discount + shipping)

    order = Order.objects.create(
        full_name=full_name,
        email=email,
        city=city,
        postal_code=postal_code,
        promo_code=promo_code if discount > 0 else '',
        subtotal=subtotal,
        discount=discount,
        shipping=shipping,
        total=total,
    )

    for it in items:
        OrderItem.objects.create(
            order=order,
            product_name=it.get('name', 'Garment'),
            variant=it.get('colour', 'Standard'),
            unit_price=Decimal(str(it['price'])),
            quantity=int(it['qty']),
        )

    return JsonResponse({
        'ok': True,
        'order_number': order.order_number,
        'total': float(order.total),
    })


@require_POST
def api_subscribe(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    email = (payload.get('email') or '').strip().lower()
    if '@' not in email:
        return JsonResponse({'error': 'Please enter a valid email'}, status=400)

    _, created = Subscriber.objects.get_or_create(email=email)
    return JsonResponse({
        'ok': True,
        'message': 'You’re on the list. Thank you!' if created else 'You’re already subscribed!'
    })



# ==========================================
# TREAD CUSTOM ADMIN PANEL
# ==========================================

class AdminLoginView(LoginView):
    template_name = 'fashion/admin/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('admin_dashboard')

    def get_success_url(self):
        return reverse_lazy('admin_dashboard')

    def form_valid(self, form):
        if not form.get_user().is_staff:
            form.add_error(None, 'You do not have admin access.')
            return self.form_invalid(form)

        return super().form_valid(form)
    

@staff_member_required(login_url='admin_login')
def admin_dashboard(request):
    total_revenue = Order.objects.aggregate(rev=Sum('total'))['rev'] or 0
    context = {
        'total_products':    Product.objects.count(),
        'in_stock_products': Product.objects.filter(in_stock=True).count(),
        'total_orders':      Order.objects.count(),
        'total_revenue':     total_revenue,
        'total_subscribers': Subscriber.objects.count(),
        'recent_orders':     Order.objects.order_by('-created_at')[:8],
        'pending_orders':    Order.objects.filter(status='pending').count(),
        'confirmed_orders':  Order.objects.filter(status='confirmed').count(),
        'shipped_orders':    Order.objects.filter(status='shipped').count(),
    }
    return render(request, 'fashion/admin/dashboard.html', context)


@staff_member_required(login_url='admin_login')
def admin_products(request):
    products = Product.objects.all().order_by('category', 'name')

    # Toggle in_stock via POST
    if request.method == 'POST':
        pk = request.POST.get('toggle_pk')
        if pk:
            p = get_object_or_404(Product, pk=pk)
            p.in_stock = not p.in_stock
            p.save()
            messages.success(request, f'"{p.name}" stock status updated.')
        return redirect('admin_products')

    return render(request, 'fashion/admin/products.html', {
        'products': products,
    })


@staff_member_required(login_url='admin_login')
def admin_orders(request):
    qs = Order.objects.order_by('-created_at')
    status_filter = request.GET.get('status', '')
    search = request.GET.get('q', '').strip()
    if status_filter:
        qs = qs.filter(status=status_filter)
    if search:
        qs = qs.filter(full_name__icontains=search) | qs.filter(order_number__icontains=search) | qs.filter(email__icontains=search)

    return render(request, 'fashion/admin/orders.html', {
        'orders': qs,
        'status_filter': status_filter,
        'search': search,
        'status_choices': Order.STATUS_CHOICES,
    })


@staff_member_required(login_url='admin_login')
def admin_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order {order.order_number} status updated to {order.get_status_display()}.')
        return redirect('admin_order_detail', pk=pk)

    return render(request, 'fashion/admin/order_detail.html', {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    })


@staff_member_required(login_url='admin_login')
def admin_subscribers(request):
    subscribers = Subscriber.objects.order_by('-subscribed_at')

    # CSV export
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'
        writer = csv.writer(response)
        writer.writerow(['Email', 'Subscribed At'])
        for s in subscribers:
            writer.writerow([s.email, s.subscribed_at.strftime('%Y-%m-%d %H:%M')])
        return response

    return render(request, 'fashion/admin/subscribers.html', {
        'subscribers': subscribers,
    })

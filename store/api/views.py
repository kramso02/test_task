import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from payments import models
from .services import get_or_create_stripe_coupon, get_or_create_stripe_tax

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_checkout_session(request, order_id):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid method"}, status=405)

    order = get_object_or_404(models.Order, id=order_id)
    line_items = []
    coupon_id = None
    tax_id = None

    if order.discount:
        coupon_id = get_or_create_stripe_coupon(order.discount)

    if order.tax:
        tax_id = get_or_create_stripe_tax(order.tax)

    for order_item in order.items.all():
        item_data = {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': order_item.item.name
                },
                'unit_amount': int(order_item.item.price * 100),
            },
            'quantity': order_item.quantity,
        }

        if tax_id:
            item_data['tax_rates'] = [tax_id]

        line_items.append(item_data)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url='http://localhost:8000/success/',
            cancel_url='http://localhost:8000/cancel/',
            discounts=[{"coupon": coupon_id}] if coupon_id else [],
        )

        return JsonResponse({"id": session.id})

    except Exception:
        return JsonResponse({"id": "test_id"})


def render_item_html(request, item_id):
    item = get_object_or_404(models.Item, id=item_id)

    return render(request, "payment.html", {
        "item": item,
        "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
    })


def success_view(request):
    return render(request, "success.html")


def cancel_view(request):
    return render(request, "cancel.html")

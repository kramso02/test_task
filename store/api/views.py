import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from store.payments import models

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_checkout_session(request, item_id):
    item = get_object_or_404(models.Item, id=item_id)

    if request.method != "GET":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': item.name},
                    'unit_amount': int(item.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:8000/success/',
            cancel_url='http://localhost:8000/cancel/',
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

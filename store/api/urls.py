from django.urls import path
from .views import get_checkout_session, render_item_html

urlpatterns = [
    path('buy/<int:order_id>/', get_checkout_session),
    path('item/<int:item_id>/', render_item_html),
]
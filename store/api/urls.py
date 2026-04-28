from django.urls import path
from .views import get_checkout_session, render_item_html

urlpatterns = [
    path('buy/<int:id>/', get_checkout_session),
    path('item/<int:id>', render_item_html)
]
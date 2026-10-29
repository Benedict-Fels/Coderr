from django.urls import path
from .views import BusinessProfileListView, CustomerProfileListView, ProfileDetailView

urlpatterns = [
    path('profile/<int:pk>/', ProfileDetailView.as_view()),
    path('profiles/business/', BusinessProfileListView.as_view()),
    path('profiles/customer/', CustomerProfileListView.as_view()),
]

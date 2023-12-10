from django.urls import path
from .views import login_view, create_account, dashboard, logout_view, edit_card, delete_card, view_all_cards, like_card, dislike_card, return_to_dashboard, filter_cards, generate_report

urlpatterns = [
    path('login/', login_view, name='login'),
    path('create_account/', create_account, name='create_account'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('edit_card/<int:card_id>/', edit_card, name='edit_card'),
    path('delete_card/<int:card_id>/', delete_card, name='delete_card'),
    path('view_all_cards/', view_all_cards, name='view_all_cards'),
    path('like_card/<int:card_id>/', like_card, name='like_card'),
    path('dislike_card/<int:card_id>/', dislike_card, name='dislike_card'),
    path('return-to-dashboard/', return_to_dashboard, name='return_to_dashboard'),
    path('filter_cards/', filter_cards, name='filter_cards'),
    path('generate_report/', generate_report, name='generate_report'),
]

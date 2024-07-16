from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 
    
urlpatterns = [
    path('', views.home, name='home'),
    path('new/', views.book_create, name='book_create'),
    path('update/<int:pk>/', views.book_update, name='book_update'),
    path('delete/<int:pk>/', views.book_delete, name='book_delete'),
    #####
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('verify-otp-reset/', views.verify_otp_reset, name='verify_otp_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='librarian/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='librarian/password_reset_complete.html'), name='password_reset_complete'),
    #####
    path('available-books/', views.available_books, name='available_books'),    
    path('issued-books/', views.issued_books, name='issued_books'),
    path('book/<int:pk>/issue/', views.issue_book, name='issue_book'),
    path('book/<int:pk>/return/', views.return_book, name='return_book'),
    path('all-books/', views.all_books, name='all_books'),
]
 
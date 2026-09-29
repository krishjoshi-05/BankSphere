from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('',              views.home,    name='home'),
    path('about/',        views.about,   name='about'),
    path('contact/',      views.contact, name='contact'),

    # Auth
    path('signup/',       views.signup,      name='signup'),
    path('login/',        views.login_view,  name='login'),
    path('logout/',       views.logout_view, name='logout'),

    # User
    path('dashboard/',        views.dashboard,           name='dashboard'),
    path('profile/',          views.profile,             name='profile'),
    path('change-password/',  views.change_password,     name='change_password'),
    path('transfer/',         views.fund_transfer,       name='fund_transfer'),
    path('transactions/',     views.transaction_history, name='transaction_history'),
    path('statement/',        views.download_statement,  name='download_statement'),

    # Admin
    path('admin-dashboard/',        views.admin_dashboard,            name='admin_dashboard'),
    path('admin-users/',            views.admin_user_management,      name='admin_user_management'),
    path('admin-users/toggle/<int:user_id>/', views.admin_toggle_user, name='admin_toggle_user'),
    path('admin-users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin-transactions/',     views.admin_transaction_monitoring, name='admin_transaction_monitoring'),
    path('admin-transactions/flag/<int:tx_id>/', views.admin_flag_transaction, name='admin_flag_transaction'),
    path('admin-report-pdf/',       views.admin_pdf_all,              name='admin_pdf_all'),
]

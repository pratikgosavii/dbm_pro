from django.urls import path
from . import views

urlpatterns = [
    # Payment URLs
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('payments/<int:payment_id>/edit/', views.payment_edit, name='payment_edit'),
    path('payments/<int:payment_id>/delete/', views.payment_delete, name='payment_delete'),
    
    # Invoice URLs
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_id>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<int:invoice_id>/delete/', views.invoice_delete, name='invoice_delete'),
    
    # Expense URLs
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:expense_id>/', views.expense_detail, name='expense_detail'),
    path('expenses/<int:expense_id>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:expense_id>/delete/', views.expense_delete, name='expense_delete'),
    path('expenses/<int:expense_id>/approve/', views.expense_approve, name='expense_approve'),
    
    # Reports
    path('reports/payment/', views.payment_report, name='payment_report'),
    path('reports/expense/', views.expense_report, name='expense_report'),
    path('reports/project-profitability/', views.project_profitability_report, name='project_profitability_report'),
]

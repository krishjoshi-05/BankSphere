from django.contrib import admin
from .models import BankUser, Transaction, ContactMessage


@admin.register(BankUser)
class BankUserAdmin(admin.ModelAdmin):
    list_display   = ('fullname', 'username', 'account_number', 'email', 'phone', 'balance', 'is_active', 'created_at')
    list_filter    = ('is_active',)
    search_fields  = ('fullname', 'username', 'email', 'account_number')
    readonly_fields = ('account_number', 'created_at')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display  = ('user', 'transaction_type', 'amount', 'details', 'status', 'flagged', 'date')
    list_filter   = ('transaction_type', 'status', 'flagged')
    search_fields = ('user__username', 'details')
    readonly_fields = ('date',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'subject', 'is_read', 'received_at')
    list_filter   = ('is_read',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'received_at')

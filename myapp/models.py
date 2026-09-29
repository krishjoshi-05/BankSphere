from django.db import models


class BankUser(models.Model):
    fullname       = models.CharField(max_length=100)
    dob            = models.DateField()
    email          = models.EmailField(unique=True)
    phone          = models.CharField(max_length=15)
    address        = models.TextField()
    username       = models.CharField(max_length=50, unique=True)
    password       = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20, unique=True, blank=True)
    balance        = models.DecimalField(max_digits=12, decimal_places=2, default=10000.00)
    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.account_number:
            last = BankUser.objects.count()
            self.account_number = str(100001 + last)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fullname} ({self.account_number})"

    class Meta:
        verbose_name = "Bank User"
        verbose_name_plural = "Bank Users"
        ordering = ['-created_at']


class Transaction(models.Model):
    TYPES = [('Credit', 'Credit'), ('Debit', 'Debit')]

    user             = models.ForeignKey(BankUser, on_delete=models.CASCADE, related_name='transactions')
    date             = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=10, choices=TYPES)
    details          = models.CharField(max_length=200, blank=True, default='Transfer')
    amount           = models.DecimalField(max_digits=12, decimal_places=2)
    status           = models.CharField(max_length=20, default='Completed')
    flagged          = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} | {self.transaction_type} | ₹{self.amount}"

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ['-date']


class ContactMessage(models.Model):
    name       = models.CharField(max_length=100)
    email      = models.EmailField()
    subject    = models.CharField(max_length=200)
    message    = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)
    is_read    = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} — {self.subject} ({self.received_at.strftime('%d %b %Y')})"

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-received_at']

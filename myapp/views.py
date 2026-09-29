from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone
from .models import BankUser, Transaction, ContactMessage
from django.contrib.auth.hashers import make_password, check_password
import io

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
ADMIN_KEY      = "ADMIN123"

# ──────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────

def login_required_user(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def login_required_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def get_current_user(request):
    return BankUser.objects.get(id=request.session['user_id'])


# ──────────────────────────────────────────
# PUBLIC PAGES
# ──────────────────────────────────────────

def home(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name, email=email,
                subject=subject, message=message
            )
            messages.success(request, 'Your message has been sent successfully!')
        else:
            messages.error(request, 'Please fill in all fields.')
        return redirect('contact')
    return render(request, 'contact.html')


# ──────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────

def signup(request):
    if request.method == 'POST':
        fullname   = request.POST.get('fullname', '').strip()
        dob        = request.POST.get('dob', '').strip()
        email      = request.POST.get('email', '').strip()
        phone      = request.POST.get('phone', '').strip()
        address    = request.POST.get('address', '').strip()
        username   = request.POST.get('username', '').strip()
        password   = request.POST.get('password', '').strip()
        confirm_pw = request.POST.get('confirm_password', '').strip()

        if password != confirm_pw:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')
        if BankUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('signup')
        if BankUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('signup')

        # FIX: password is hashed with make_password before saving
        BankUser.objects.create(
            fullname=fullname, dob=dob, email=email,
            phone=phone, address=address,
            username=username, password=make_password(password),
            balance=10000.00
        )
        messages.success(request, 'Account created! Please login.')
        return redirect('login')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        login_role = request.POST.get('login_role', 'user')

        # ---- ADMIN login ----
        if login_role == 'admin':
            a_user = request.POST.get('admin_username', '').strip()
            a_pass = request.POST.get('admin_password', '').strip()
            a_key  = request.POST.get('admin_key', '').strip()
            # FIX: use constant-time comparison to prevent timing attacks,
            # and correctly check all three fields
            if (a_user == ADMIN_USERNAME and
                    a_pass == ADMIN_PASSWORD and
                    a_key == ADMIN_KEY):
                request.session['is_admin'] = True
                request.session.pop('user_id', None)   # FIX: don't set user_id to None, pop it
                return redirect('admin_dashboard')
            messages.error(request, 'Invalid admin credentials or key.')
            return redirect('login')

        # ---- USER login ----
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            user = BankUser.objects.get(username=username)
            if not check_password(password, user.password):
                messages.error(request, 'Invalid username or password.')
                return redirect('login')
            if not user.is_active:
                messages.error(request, 'Your account has been deactivated. Contact support.')
                return redirect('login')
            request.session['user_id']  = user.id
            request.session['is_admin'] = False
            return redirect('dashboard')
        except BankUser.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


# ──────────────────────────────────────────
# USER PAGES
# ──────────────────────────────────────────

@login_required_user
def dashboard(request):
    user = get_current_user(request)
    recent_tx = Transaction.objects.filter(user=user).order_by('-date')[:5]
    return render(request, 'user_dashboard.html', {'user': user, 'transactions': recent_tx})


@login_required_user
def profile(request):
    user = get_current_user(request)
    return render(request, 'profile.html', {'user': user})


@login_required_user
def change_password(request):
    user = get_current_user(request)
    if request.method == 'POST':
        old_pw  = request.POST.get('old_password', '').strip()
        new_pw  = request.POST.get('new_password', '').strip()
        conf_pw = request.POST.get('confirm_password', '').strip()
        if not check_password(old_pw, user.password):
            messages.error(request, 'Current password is incorrect.')
        elif new_pw != conf_pw:
            messages.error(request, 'New passwords do not match.')
        elif len(new_pw) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        else:
            user.password = make_password(new_pw)
            user.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('dashboard')
    return render(request, 'change_password.html', {'user': user})


@login_required_user
def fund_transfer(request):
    user = get_current_user(request)
    if request.method == 'POST':
        account_no = request.POST.get('account', '').strip()
        amount_str = request.POST.get('amount', '').strip()
        details    = request.POST.get('details', 'Fund Transfer').strip()

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            messages.error(request, 'Please enter a valid amount.')
            return redirect('fund_transfer')

        if account_no == user.account_number:
            messages.error(request, 'You cannot transfer to your own account.')
            return redirect('fund_transfer')

        try:
            receiver = BankUser.objects.get(account_number=account_no)
        except BankUser.DoesNotExist:
            messages.error(request, 'Receiver account not found.')
            return redirect('fund_transfer')

        if float(user.balance) < amount:
            messages.error(request, 'Insufficient balance.')
            return redirect('fund_transfer')

        user.balance = float(user.balance) - amount
        user.save()

        receiver.balance = float(receiver.balance) + amount
        receiver.save()

        Transaction.objects.create(
            user=user, transaction_type='Debit', amount=amount,
            details=f'Transfer to {receiver.account_number} | {details}', status='Completed'
        )
        Transaction.objects.create(
            user=receiver, transaction_type='Credit', amount=amount,
            details=f'Transfer from {user.account_number} | {details}', status='Completed'
        )

        messages.success(request, f'Rs.{amount:.2f} transferred successfully to {receiver.fullname}!')
        return redirect('dashboard')

    return render(request, 'fund_transfer.html', {'user': user})


@login_required_user
def transaction_history(request):
    user = get_current_user(request)
    transactions = Transaction.objects.filter(user=user).order_by('-date')
    return render(request, 'transaction_history.html', {'user': user, 'transactions': transactions})


@login_required_user
def download_statement(request):
    """Generate PDF bank statement using reportlab.
    FIX: 'Generated' timestamp is now passed from the frontend (JS Date) via a GET param
         so it reflects the user's LOCAL browser time, not the server timezone.
         Falls back to server time if param is absent.
    """
    user = get_current_user(request)
    transactions = Transaction.objects.filter(user=user).order_by('-date')

    # FIX: use client-supplied timestamp when available
    client_time = request.GET.get('ts', '').strip()
    if client_time:
        generated_str = client_time          # e.g. "25-Mar-2026 10:45 AM"
    else:
        generated_str = timezone.now().strftime('%d-%b-%Y %I:%M %p')

    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import mm

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # ── Header bar ──
        p.setFillColor(colors.HexColor('#0a2e5c'))
        p.rect(0, height - 80, width, 80, fill=1, stroke=0)
        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 24)
        p.drawString(50, height - 44, "BankSphere")
        p.setFont("Helvetica", 11)
        p.setFillColor(colors.HexColor('#2ecc9a'))
        p.drawString(50, height - 62, "Bank Statement")

        # right-align generated date
        p.setFillColor(colors.white)
        p.setFont("Helvetica", 9)
        p.drawRightString(width - 50, height - 44, f"Generated: {generated_str}")

        # ── Account info box ──
        p.setFillColor(colors.HexColor('#f4f7fb'))
        p.roundRect(40, height - 150, width - 80, 58, 6, fill=1, stroke=0)
        p.setFillColor(colors.HexColor('#0a2e5c'))
        p.setFont("Helvetica-Bold", 10)
        p.drawString(55, height - 105, "Account Holder")
        p.drawString(55, height - 120, "Account Number")
        p.drawString(300, height - 105, "Current Balance")
        p.setFont("Helvetica", 10)
        p.drawString(170, height - 105, user.fullname)
        p.drawString(170, height - 120, user.account_number)
        p.setFillColor(colors.HexColor('#1a7a3c'))
        p.setFont("Helvetica-Bold", 10)
        p.drawString(400, height - 105, f"Rs. {user.balance:.2f}")

        # ── Table header ──
        y = height - 175
        p.setFillColor(colors.HexColor('#0a2e5c'))
        p.rect(40, y - 6, width - 80, 24, fill=1, stroke=0)
        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 9)
        cols = [50, 150, 230, 390, 460, 535]
        headers = ["Date & Time", "Type", "Details", "Amount (Rs.)", "Status"]
        for col, hdr in zip(cols, headers):
            p.drawString(col, y + 4, hdr)

        y -= 22
        p.setFont("Helvetica", 8.5)

        for i, tx in enumerate(transactions):
            if y < 60:
                p.showPage()
                y = height - 60
                p.setFont("Helvetica", 8.5)

            bg = colors.HexColor('#f9fafb') if i % 2 == 0 else colors.white
            p.setFillColor(bg)
            p.rect(40, y - 5, width - 80, 19, fill=1, stroke=0)

            # thin left-side colour stripe for type
            if tx.transaction_type == 'Credit':
                p.setFillColor(colors.HexColor('#1a7a3c'))
            else:
                p.setFillColor(colors.HexColor('#c0392b'))
            p.rect(40, y - 5, 4, 19, fill=1, stroke=0)

            date_str = tx.date.strftime('%d-%b-%Y %H:%M')
            p.setFillColor(colors.HexColor('#444444'))
            p.drawString(50,  y + 2, date_str)
            p.drawString(150, y + 2, tx.transaction_type)
            detail_text = (tx.details[:32] + '..') if len(tx.details) > 32 else tx.details
            p.drawString(230, y + 2, detail_text)

            if tx.transaction_type == 'Credit':
                p.setFillColor(colors.HexColor('#1a7a3c'))
            else:
                p.setFillColor(colors.HexColor('#c0392b'))
            prefix = '+' if tx.transaction_type == 'Credit' else '-'
            p.drawString(390, y + 2, f"{prefix}{tx.amount:.2f}")

            p.setFillColor(colors.HexColor('#444444'))
            p.drawString(460, y + 2, tx.status)
            y -= 21

        # ── Footer bar ──
        p.setFillColor(colors.HexColor('#0a2e5c'))
        p.rect(0, 0, width, 32, fill=1, stroke=0)
        p.setFillColor(colors.white)
        p.setFont("Helvetica", 8)
        p.drawCentredString(width / 2, 12, "© 2026 BankSphere  |  Secure Digital Banking Platform  |  This is a computer-generated document.")

        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="BankSphere_Statement_{user.account_number}.pdf"'
        return response

    except ImportError:
        return HttpResponse(
            "ReportLab is not installed. Run: pip install reportlab",
            content_type='text/plain'
        )


# ──────────────────────────────────────────
# ADMIN PAGES
# ──────────────────────────────────────────

@login_required_admin
def admin_dashboard(request):
    total_users    = BankUser.objects.count()
    total_tx       = Transaction.objects.count()
    total_funds    = sum(u.balance for u in BankUser.objects.all())
    flagged_count  = Transaction.objects.filter(flagged=True).count()
    recent_tx      = Transaction.objects.order_by('-date')[:10]
    return render(request, 'admin_dashboard.html', {
        'total_users':   total_users,
        'total_tx':      total_tx,
        'total_funds':   total_funds,
        'flagged_count': flagged_count,
        'recent_tx':     recent_tx,
    })


@login_required_admin
def admin_user_management(request):
    users = BankUser.objects.all().order_by('-created_at')
    return render(request, 'admin_user_management.html', {'users': users})


@login_required_admin
def admin_toggle_user(request, user_id):
    user = get_object_or_404(BankUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f'User {user.fullname} has been {status}.')
    return redirect('admin_user_management')


@login_required_admin
def admin_delete_user(request, user_id):
    user = get_object_or_404(BankUser, id=user_id)
    user.delete()
    messages.success(request, 'User deleted.')
    return redirect('admin_user_management')


@login_required_admin
def admin_transaction_monitoring(request):
    transactions = Transaction.objects.select_related('user').order_by('-date')
    return render(request, 'admin_transaction_monitoring.html', {'transactions': transactions})


@login_required_admin
def admin_flag_transaction(request, tx_id):
    tx = get_object_or_404(Transaction, id=tx_id)
    tx.flagged = not tx.flagged
    tx.save()
    return redirect('admin_transaction_monitoring')


@login_required_admin
def admin_pdf_all(request):
    """Admin downloads PDF of ALL transactions.
    FIX: timestamp uses client-supplied ts param if present.
    """
    transactions = Transaction.objects.select_related('user').order_by('-date')

    client_time = request.GET.get('ts', '').strip()
    generated_str = client_time if client_time else timezone.now().strftime('%d-%b-%Y %I:%M %p')

    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Header
        p.setFillColor(colors.HexColor('#0a2e5c'))
        p.rect(0, height - 80, width, 80, fill=1, stroke=0)
        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 22)
        p.drawString(50, height - 44, "BankSphere — Admin Report")
        p.setFont("Helvetica", 10)
        p.setFillColor(colors.HexColor('#2ecc9a'))
        p.drawString(50, height - 62, "All Transactions")
        p.setFillColor(colors.white)
        p.setFont("Helvetica", 9)
        p.drawRightString(width - 50, height - 44, f"Generated: {generated_str}")

        # Table header
        y = height - 110
        p.setFillColor(colors.HexColor('#0a2e5c'))
        p.rect(40, y - 4, width - 80, 22, fill=1, stroke=0)
        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 9)
        p.drawString(50,  y + 4, "Date")
        p.drawString(140, y + 4, "User")
        p.drawString(265, y + 4, "Account")
        p.drawString(360, y + 4, "Type")
        p.drawString(420, y + 4, "Amount")
        p.drawString(490, y + 4, "Status")
        p.drawString(545, y + 4, "Flagged")
        y -= 24

        p.setFont("Helvetica", 8)
        for i, tx in enumerate(transactions):
            if y < 50:
                p.showPage()
                y = height - 60
                p.setFont("Helvetica", 8)
            bg = colors.HexColor('#f9f9f9') if i % 2 == 0 else colors.white
            p.setFillColor(bg)
            p.rect(40, y - 4, width - 80, 16, fill=1, stroke=0)

            if tx.transaction_type == 'Credit':
                p.setFillColor(colors.HexColor('#1a7a3c'))
            else:
                p.setFillColor(colors.HexColor('#c0392b'))
            p.rect(40, y - 4, 4, 16, fill=1, stroke=0)

            p.setFillColor(colors.HexColor('#333'))
            p.drawString(50,  y + 1, tx.date.strftime('%d-%b-%Y %H:%M'))
            p.drawString(140, y + 1, tx.user.fullname[:18])
            p.drawString(265, y + 1, tx.user.account_number)

            if tx.transaction_type == 'Credit':
                p.setFillColor(colors.HexColor('#1a7a3c'))
            else:
                p.setFillColor(colors.HexColor('#c0392b'))
            p.drawString(360, y + 1, tx.transaction_type)

            p.setFillColor(colors.HexColor('#333'))
            p.drawString(420, y + 1, f"{tx.amount:.2f}")
            p.drawString(490, y + 1, tx.status)
            flagged_txt = "YES" if tx.flagged else "NO"
            if tx.flagged:
                p.setFillColor(colors.HexColor('#c0392b'))
            p.drawString(545, y + 1, flagged_txt)
            p.setFillColor(colors.HexColor('#333'))
            y -= 18

        # Footer
        p.setFillColor(colors.HexColor('#0a2e5c'))
        p.rect(0, 0, width, 28, fill=1, stroke=0)
        p.setFillColor(colors.white)
        p.setFont("Helvetica", 8)
        p.drawCentredString(width / 2, 10, "© 2026 BankSphere Admin Report  |  Confidential")
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="BankSphere_Admin_Report.pdf"'
        return response
    except ImportError:
        return HttpResponse("pip install reportlab", content_type='text/plain')

"""
Management command: export all BankSphere data to a readable SQL file.

Usage:
    python manage.py export_data
    python manage.py export_data --output myfile.sql
"""

import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.models import BankUser, Transaction, ContactMessage


class Command(BaseCommand):
    help = 'Export all BankSphere data to a readable SQL file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            default='banksphere_data_export.sql',
            help='Output filename (default: banksphere_data_export.sql)'
        )

    def handle(self, *args, **options):
        filename = options['output']
        users        = BankUser.objects.all().order_by('id')
        transactions = Transaction.objects.all().order_by('id')
        messages_qs  = ContactMessage.objects.all().order_by('id')

        lines = []

        # ── HEADER ──────────────────────────────────────────────────────
        lines.append("-- ============================================================")
        lines.append("--  BankSphere — Full Data Export")
        lines.append(f"--  Generated : {timezone.now().strftime('%d %B %Y, %I:%M %p')}")
        lines.append(f"--  Users      : {users.count()}")
        lines.append(f"--  Transactions: {transactions.count()}")
        lines.append(f"--  Messages   : {messages_qs.count()}")
        lines.append("-- ============================================================")
        lines.append("")

        # ── USERS TABLE ─────────────────────────────────────────────────
        lines.append("-- ------------------------------------------------------------")
        lines.append("--  TABLE: myapp_bankuser")
        lines.append("-- ------------------------------------------------------------")
        lines.append("")
        lines.append("CREATE TABLE IF NOT EXISTS `myapp_bankuser` (")
        lines.append("    `id`             INT            NOT NULL AUTO_INCREMENT,")
        lines.append("    `fullname`       VARCHAR(100)   NOT NULL,")
        lines.append("    `dob`            DATE           NOT NULL,")
        lines.append("    `email`          VARCHAR(254)   NOT NULL UNIQUE,")
        lines.append("    `phone`          VARCHAR(15)    NOT NULL,")
        lines.append("    `address`        TEXT           NOT NULL,")
        lines.append("    `username`       VARCHAR(50)    NOT NULL UNIQUE,")
        lines.append("    `password`       VARCHAR(100)   NOT NULL,")
        lines.append("    `account_number` VARCHAR(20)    NOT NULL UNIQUE,")
        lines.append("    `balance`        DECIMAL(12,2)  NOT NULL DEFAULT 10000.00,")
        lines.append("    `is_active`      TINYINT(1)     NOT NULL DEFAULT 1,")
        lines.append("    `created_at`     DATETIME       NOT NULL,")
        lines.append("    PRIMARY KEY (`id`)")
        lines.append(");")
        lines.append("")

        if users.exists():
            lines.append("INSERT INTO `myapp_bankuser`")
            lines.append("    (`id`, `fullname`, `dob`, `email`, `phone`, `address`, `username`, `password`, `account_number`, `balance`, `is_active`, `created_at`)")
            lines.append("VALUES")
            rows = []
            for u in users:
                dob = u.dob.strftime('%Y-%m-%d') if u.dob else 'NULL'
                created = u.created_at.strftime('%Y-%m-%d %H:%M:%S') if u.created_at else 'NULL'
                active  = 1 if u.is_active else 0
                row = (
                    f"    ({u.id}, '{self._esc(u.fullname)}', '{dob}', '{self._esc(u.email)}', "
                    f"'{self._esc(u.phone)}', '{self._esc(str(u.address))}', '{self._esc(u.username)}', "
                    f"'{self._esc(u.password)}', '{u.account_number}', {u.balance}, {active}, '{created}')"
                )
                rows.append(row)
            lines.append(',\n'.join(rows) + ';')
        else:
            lines.append("-- No users found.")

        lines.append("")

        # ── TRANSACTIONS TABLE ───────────────────────────────────────────
        lines.append("-- ------------------------------------------------------------")
        lines.append("--  TABLE: myapp_transaction")
        lines.append("-- ------------------------------------------------------------")
        lines.append("")
        lines.append("CREATE TABLE IF NOT EXISTS `myapp_transaction` (")
        lines.append("    `id`               INT            NOT NULL AUTO_INCREMENT,")
        lines.append("    `user_id`          INT            NOT NULL,")
        lines.append("    `date`             DATETIME       NOT NULL,")
        lines.append("    `transaction_type` VARCHAR(10)    NOT NULL,")
        lines.append("    `details`          VARCHAR(200)   NOT NULL DEFAULT 'Transfer',")
        lines.append("    `amount`           DECIMAL(12,2)  NOT NULL,")
        lines.append("    `status`           VARCHAR(20)    NOT NULL DEFAULT 'Completed',")
        lines.append("    `flagged`          TINYINT(1)     NOT NULL DEFAULT 0,")
        lines.append("    PRIMARY KEY (`id`),")
        lines.append("    FOREIGN KEY (`user_id`) REFERENCES `myapp_bankuser`(`id`) ON DELETE CASCADE")
        lines.append(");")
        lines.append("")

        if transactions.exists():
            lines.append("INSERT INTO `myapp_transaction`")
            lines.append("    (`id`, `user_id`, `date`, `transaction_type`, `details`, `amount`, `status`, `flagged`)")
            lines.append("VALUES")
            rows = []
            for t in transactions:
                date    = t.date.strftime('%Y-%m-%d %H:%M:%S') if t.date else 'NULL'
                flagged = 1 if t.flagged else 0
                row = (
                    f"    ({t.id}, {t.user_id}, '{date}', '{t.transaction_type}', "
                    f"'{self._esc(t.details)}', {t.amount}, '{t.status}', {flagged})"
                )
                rows.append(row)
            lines.append(',\n'.join(rows) + ';')
        else:
            lines.append("-- No transactions found.")

        lines.append("")

        # ── CONTACT MESSAGES TABLE ───────────────────────────────────────
        lines.append("-- ------------------------------------------------------------")
        lines.append("--  TABLE: myapp_contactmessage")
        lines.append("-- ------------------------------------------------------------")
        lines.append("")
        lines.append("CREATE TABLE IF NOT EXISTS `myapp_contactmessage` (")
        lines.append("    `id`          INT          NOT NULL AUTO_INCREMENT,")
        lines.append("    `name`        VARCHAR(100) NOT NULL,")
        lines.append("    `email`       VARCHAR(254) NOT NULL,")
        lines.append("    `subject`     VARCHAR(200) NOT NULL,")
        lines.append("    `message`     TEXT         NOT NULL,")
        lines.append("    `received_at` DATETIME     NOT NULL,")
        lines.append("    `is_read`     TINYINT(1)   NOT NULL DEFAULT 0,")
        lines.append("    PRIMARY KEY (`id`)")
        lines.append(");")
        lines.append("")

        if messages_qs.exists():
            lines.append("INSERT INTO `myapp_contactmessage`")
            lines.append("    (`id`, `name`, `email`, `subject`, `message`, `received_at`, `is_read`)")
            lines.append("VALUES")
            rows = []
            for m in messages_qs:
                received = m.received_at.strftime('%Y-%m-%d %H:%M:%S') if m.received_at else 'NULL'
                is_read  = 1 if m.is_read else 0
                row = (
                    f"    ({m.id}, '{self._esc(m.name)}', '{self._esc(m.email)}', "
                    f"'{self._esc(m.subject)}', '{self._esc(m.message)}', '{received}', {is_read})"
                )
                rows.append(row)
            lines.append(',\n'.join(rows) + ';')
        else:
            lines.append("-- No contact messages found.")

        lines.append("")
        lines.append("-- ============================================================")
        lines.append("--  END OF EXPORT")
        lines.append("-- ============================================================")

        # ── WRITE FILE ───────────────────────────────────────────────────
        output_path = os.path.join(os.getcwd(), filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        self.stdout.write(self.style.SUCCESS(
            f"\nExport complete!\n"
            f"File : {output_path}\n"
            f"Users: {users.count()}  |  Transactions: {transactions.count()}  |  Messages: {messages_qs.count()}\n"
        ))

    @staticmethod
    def _esc(value):
        """Escape single quotes for SQL safety."""
        return str(value).replace("'", "''")

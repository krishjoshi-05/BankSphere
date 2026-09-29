-- ============================================================
--  BankSphere - MySQL Database Schema & Sample Data
--  Compatible with: MySQL 8.0+ / MariaDB 10.5+
--  Project: BankSphere Bank Management System (Django)
--  Created: 2026
-- ============================================================

-- CREATE DATABASE
CREATE DATABASE IF NOT EXISTS banksphere_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE banksphere_db;

-- ============================================================
--  TABLE: myapp_bankuser
--  Maps to Django model: BankUser
-- ============================================================
CREATE TABLE IF NOT EXISTS `myapp_bankuser` (
    `id`             INT            NOT NULL AUTO_INCREMENT,
    `fullname`       VARCHAR(100)   NOT NULL,
    `dob`            DATE           NOT NULL,
    `email`          VARCHAR(254)   NOT NULL UNIQUE,
    `phone`          VARCHAR(15)    NOT NULL,
    `address`        TEXT           NOT NULL,
    `username`       VARCHAR(50)    NOT NULL UNIQUE,
    `password`       VARCHAR(100)   NOT NULL,
    `account_number` VARCHAR(20)    NOT NULL UNIQUE,
    `balance`        DECIMAL(12,2)  NOT NULL DEFAULT 10000.00,
    `is_active`      TINYINT(1)     NOT NULL DEFAULT 1,
    `created_at`     DATETIME(6)    NOT NULL,
    PRIMARY KEY (`id`),
    INDEX `idx_username`       (`username`),
    INDEX `idx_email`          (`email`),
    INDEX `idx_account_number` (`account_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
--  TABLE: myapp_transaction
--  Maps to Django model: Transaction
-- ============================================================
CREATE TABLE IF NOT EXISTS `myapp_transaction` (
    `id`               INT            NOT NULL AUTO_INCREMENT,
    `user_id`          INT            NOT NULL,
    `date`             DATETIME(6)    NOT NULL,
    `transaction_type` VARCHAR(10)    NOT NULL,   -- 'Credit' or 'Debit'
    `details`          VARCHAR(200)   NOT NULL DEFAULT 'Transfer',
    `amount`           DECIMAL(12,2)  NOT NULL,
    `status`           VARCHAR(20)    NOT NULL DEFAULT 'Completed',
    `flagged`          TINYINT(1)     NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_transaction_user`
        FOREIGN KEY (`user_id`) REFERENCES `myapp_bankuser`(`id`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX `idx_user_id`   (`user_id`),
    INDEX `idx_date`      (`date`),
    INDEX `idx_flagged`   (`flagged`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
--  SAMPLE DATA: Users
--  Passwords stored as plain text here for demo purposes.
--  In production Django hashes these with PBKDF2.
-- ============================================================
INSERT INTO `myapp_bankuser`
    (`fullname`, `dob`, `email`, `phone`, `address`, `username`, `password`, `account_number`, `balance`, `is_active`, `created_at`)
VALUES
    ('Aarav Sharma',    '2002-04-15', 'aarav.sharma@email.com',    '9876543210', '12, Gandhi Nagar, Ahmedabad, Gujarat',      'aarav123',   'pass1234',  '100001', 18500.00, 1, NOW()),
    ('Priya Patel',     '2001-09-22', 'priya.patel@email.com',     '9812345678', '45, Sector 7, Surat, Gujarat',              'priya_p',    'priya2001', '100002', 25000.00, 1, NOW()),
    ('Rohan Mehta',     '2003-01-10', 'rohan.mehta@email.com',     '9923456789', '78, MG Road, Vadodara, Gujarat',            'rohan_m',    'rohan@123', '100003',  9200.00, 1, NOW()),
    ('Sneha Joshi',     '2000-07-05', 'sneha.joshi@email.com',     '9034567890', '3, Ashram Road, Ahmedabad, Gujarat',        'sneha_j',    'sneha456',  '100004', 32000.00, 1, NOW()),
    ('Karan Desai',     '2002-11-28', 'karan.desai@email.com',     '9145678901', '22, Civil Lines, Rajkot, Gujarat',          'karan_d',    'karan789',  '100005',  5700.00, 1, NOW()),
    ('Meera Nair',      '1999-03-17', 'meera.nair@email.com',      '9256789012', '9, Park Street, Mumbai, Maharashtra',       'meera_n',    'meera2000', '100006', 41200.00, 1, NOW()),
    ('Arjun Singh',     '2001-06-30', 'arjun.singh@email.com',     '9367890123', '67, Connaught Place, New Delhi',            'arjun_s',    'arjun@321', '100007', 15800.00, 1, NOW()),
    ('Divya Reddy',     '2003-08-14', 'divya.reddy@email.com',     '9478901234', '18, Jubilee Hills, Hyderabad, Telangana',   'divya_r',    'divya111',  '100008',  8400.00, 1, NOW()),
    ('Vikram Rao',      '2000-12-01', 'vikram.rao@email.com',      '9589012345', '54, Brigade Road, Bangalore, Karnataka',   'vikram_r',   'vikram@99', '100009', 60500.00, 1, NOW()),
    ('Ananya Gupta',    '2002-05-20', 'ananya.gupta@email.com',    '9690123456', '31, Civil Lines, Allahabad, UP',            'ananya_g',   'ananya22',  '100010', 11300.00, 0, NOW());

-- ============================================================
--  SAMPLE DATA: Transactions
-- ============================================================
INSERT INTO `myapp_transaction`
    (`user_id`, `date`, `transaction_type`, `details`, `amount`, `status`, `flagged`)
VALUES
    -- Aarav (user_id=1)
    (1, NOW() - INTERVAL 10 DAY, 'Credit', 'Initial Deposit',           10000.00, 'Completed', 0),
    (1, NOW() - INTERVAL 8  DAY, 'Credit', 'Transfer from Priya Patel',  8500.00, 'Completed', 0),
    (1, NOW() - INTERVAL 5  DAY, 'Debit',  'Fund Transfer to Rohan',     5000.00, 'Completed', 0),
    (1, NOW() - INTERVAL 2  DAY, 'Credit', 'Salary Credit',              5000.00, 'Completed', 0),

    -- Priya (user_id=2)
    (2, NOW() - INTERVAL 9  DAY, 'Credit', 'Initial Deposit',           10000.00, 'Completed', 0),
    (2, NOW() - INTERVAL 8  DAY, 'Debit',  'Transfer to Aarav Sharma',   8500.00, 'Completed', 0),
    (2, NOW() - INTERVAL 3  DAY, 'Credit', 'Scholarship Credit',        23500.00, 'Completed', 0),

    -- Rohan (user_id=3)
    (3, NOW() - INTERVAL 7  DAY, 'Credit', 'Initial Deposit',           10000.00, 'Completed', 0),
    (3, NOW() - INTERVAL 5  DAY, 'Credit', 'Received from Aarav',        5000.00, 'Completed', 0),
    (3, NOW() - INTERVAL 1  DAY, 'Debit',  'College Fee Payment',        5800.00, 'Completed', 0),

    -- Sneha (user_id=4)
    (4, NOW() - INTERVAL 6  DAY, 'Credit', 'Initial Deposit',           10000.00, 'Completed', 0),
    (4, NOW() - INTERVAL 4  DAY, 'Credit', 'Freelance Income',          22000.00, 'Completed', 0),

    -- Karan (user_id=5)
    (5, NOW() - INTERVAL 5  DAY, 'Credit', 'Initial Deposit',           10000.00, 'Completed', 0),
    (5, NOW() - INTERVAL 2  DAY, 'Debit',  'Online Shopping',            4300.00, 'Completed', 0),

    -- Vikram (user_id=9) — flagged suspicious large transfer
    (9, NOW() - INTERVAL 3  DAY, 'Credit', 'Initial Deposit',           10000.00, 'Completed', 0),
    (9, NOW() - INTERVAL 1  DAY, 'Credit', 'Large Incoming Transfer',   50500.00, 'Completed', 1),  -- flagged

    -- Ananya (user_id=10) — inactive account
    (10, NOW() - INTERVAL 15 DAY, 'Credit', 'Initial Deposit',          10000.00, 'Completed', 0),
    (10, NOW() - INTERVAL 14 DAY, 'Debit',  'Subscription Payment',       700.00, 'Completed', 0);

-- ============================================================
--  VIEWS (optional helper queries for admin reporting)
-- ============================================================

-- View: User summary with transaction count
CREATE OR REPLACE VIEW `vw_user_summary` AS
    SELECT
        u.id,
        u.fullname,
        u.username,
        u.account_number,
        u.balance,
        u.is_active,
        COUNT(t.id)                                              AS total_transactions,
        SUM(CASE WHEN t.transaction_type = 'Credit' THEN t.amount ELSE 0 END) AS total_credited,
        SUM(CASE WHEN t.transaction_type = 'Debit'  THEN t.amount ELSE 0 END) AS total_debited
    FROM `myapp_bankuser` u
    LEFT JOIN `myapp_transaction` t ON t.user_id = u.id
    GROUP BY u.id;

-- View: Flagged transactions
CREATE OR REPLACE VIEW `vw_flagged_transactions` AS
    SELECT
        t.id,
        t.date,
        t.transaction_type,
        t.details,
        t.amount,
        u.fullname,
        u.account_number
    FROM `myapp_transaction` t
    JOIN `myapp_bankuser` u ON u.id = t.user_id
    WHERE t.flagged = 1
    ORDER BY t.date DESC;

-- ============================================================
--  HOW TO USE WITH DJANGO
--  -------------------------------------------------------
--  1. Install mysqlclient:
--       pip install mysqlclient
--
--  2. Update banksphere_project/settings.py DATABASES block:
--
--       DATABASES = {
--           'default': {
--               'ENGINE':   'django.db.backends.mysql',
--               'NAME':     'banksphere_db',
--               'USER':     'your_mysql_user',
--               'PASSWORD': 'your_mysql_password',
--               'HOST':     'localhost',
--               'PORT':     '3306',
--               'OPTIONS':  {'charset': 'utf8mb4'},
--           }
--       }
--
--  3. Import this schema:
--       mysql -u root -p < banksphere_mysql.sql
--
--  4. Run Django migrations (to create Django system tables):
--       python manage.py migrate
--
--  NOTE: This SQL file creates the app tables directly.
--        Django migrations will detect existing tables and
--        skip re-creating them (fake the initial migration):
--       python manage.py migrate --fake-initial
-- ============================================================

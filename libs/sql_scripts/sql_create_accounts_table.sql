
CREATE TABLE IF NOT EXISTS Accounts (
    AccountId INT PRIMARY KEY,
    AccountName TEXT UNIQUE NOT NULL,
    AccountType TEXT NULL,
    AccountScore INT NULL,
    Icon TEXT NOT NULL,
    Description TEXT NULL
)

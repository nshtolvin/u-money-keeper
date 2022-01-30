
CREATE TABLE IF NOT EXISTS Transactions (
    TransactionId INTEGER PRIMARY KEY,
    AccountId INTEGER NULL,
    CategoryId INTEGER NOT NULL,
    DateKey INTEGER NOT NULL,
    TransactionScore INTEGER NOT NULL,
    TransactionNote TEXT NULL
)

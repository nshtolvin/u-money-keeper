
CREATE TABLE IF NOT EXISTS Categories (
    CategoryId INT PRIMARY KEY,
    CategoryName TEXT UNIQUE NOT NULL,
    Icon TEXT NOT NULL,
    CategoryColor TEXT NULL,
    Description TEXT NULL,
    FlowType INT DEFAULT -1
)

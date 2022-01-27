
CREATE TABLE IF NOT EXISTS DimDate (
    DateKey INT UNIQUE NOT NULL,
    ShortDateKey INT NOT NULL,
    FullDate DATE NOT NULL,
    WeekDayName TEXT NOT NULL,
    Quarter TEXT NOT NULL,
    Year INT NOT NULL,
    Month INT NOT NULL,
    MonthName TEXT NOT NULL,
    Day INT NOT NULL
)

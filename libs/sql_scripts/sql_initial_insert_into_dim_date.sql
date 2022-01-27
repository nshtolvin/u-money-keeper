
INSERT OR ignore
INTO DimDate (DateKey, ShortDateKey, FullDate, WeekDayName, Quarter, Year, Month, MonthName, Day)
SELECT *
FROM (
    WITH RECURSIVE dates(date) AS (
        VALUES('2021-01-01')
        UNION ALL
        SELECT date(date, '+1 day')
        FROM dates
        WHERE date < '2039-01-01'
    )
    SELECT
        CAST(strftime('%Y%m%d', date) AS INT) as DateKey
        ,CAST(strftime('%Y%m', date) AS INT) as ShortDateKey
        ,date as FullDate
        ,CASE (CAST(strftime('%w', date) AS INT) + 6) % 7
            WHEN 0 THEN 'Monday'
            WHEN 1 THEN 'Tuesday'
            WHEN 2 THEN 'Wednesday'
            WHEN 3 THEN 'Thursday'
            WHEN 4 THEN 'Friday'
            WHEN 5 THEN 'Saturday'
            ELSE 'Sunday'
        END AS DayOfWeek
        ,CASE
            WHEN CAST(strftime('%m', date) AS INT) BETWEEN 1 AND 3 THEN 'Q1'
            WHEN CAST(strftime('%m', date) AS INT) BETWEEN 4 AND 6 THEN 'Q2'
            WHEN CAST(strftime('%m', date) AS INT) BETWEEN 7 AND 9 THEN 'Q3'
            ELSE 'Q4'
        END AS Quarter
        ,CAST(strftime('%Y', date) AS INT) AS Year
        ,CAST(strftime('%m', date) AS INT) AS Month
        ,CASE CAST(strftime('%m', date) AS INT)
            WHEN 1 THEN 'January'
            WHEN 2 THEN 'February'
            WHEN 3 THEN 'March'
            WHEN 4 THEN 'April'
            WHEN 5 THEN 'May'
            WHEN 6 THEN 'June'
            WHEN 7 THEN 'July'
            WHEN 8 THEN 'August'
            WHEN 9 THEN 'September'
            WHEN 10 THEN 'October'
            WHEN 11 THEN 'November'
            WHEN 12 THEN 'December'
        END AS MonthName
        ,CAST(strftime('%d', date) AS INT) AS Day
    FROM dates
)

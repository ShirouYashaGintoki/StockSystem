SELECT *
FROM stocktables.aapl5min
WHERE selector = "BUY" OR selector = "SELL"
ORDER BY datetime DESC;
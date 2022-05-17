Select * From orcl5min;

Select datetime, assetname, close, selector, Count(*) From orcl5min
Group by datetime, assetname, close, selector
Having Count(*) > 1;

DELETE FROM stocktables.orcl5min
WHERE rowid NOT IN (
SELECT * FROM (SELECT Max(rowid) 
FROM orcl5min GROUP BY datetime, assetname, close, selector) AS t);
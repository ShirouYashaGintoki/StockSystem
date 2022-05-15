Select * From orcl5min;

Select datetime, assetname, close, selector, Count(*) From orcl5min
Group by datetime, assetname, close, selector
Having Count(*) > 1;

Delete From stocktables.orcl5min
where rowid not in (
Select * From (Select Max(rowid) 
From orcl5min Group By datetime, assetname, close, selector) as t);
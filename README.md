# Futures_data_processing
## Target
輸入時間(年月日時分)，抓取出此時此刻的價格及委託量(上下五檔)，並輸出成 pandas dataframe，最終目標給定一段時間，輸出這段時間的價格以及委託量(上下五檔)，並且速度越快越好。
## TODO
- [x] 指定日期(時間在8.45之後)，輸出結果
- [x] 指定日期及台指近一近二近三(時間在8.45之後)，輸出結果
- [x] 當指定日期在8.45之前，抓取前一天最後收盤價作為現價，輸出結果(前一天非休市日或假日)
- [x] 當指定日期在8.45之前且前一天為假日或休市日，繼續往前取，直到取到資料
- [ ] 輸入一段時間，輸出一筆Dataframe(n, 11, 3)的資料

## Result
![](https://i.imgur.com/J76k7iS.jpg)

### 9/26 (Mon) 10.50 a.m. <font face = 微軟正黑體>台指期近一</font>
```python
if __name__ == '__main__':
    txf_data = TXF_data(2016, 9, 26, 10, 50, 1) # format = (y,m,d,h,m, N(1~3))
    result = txf_data.result
    data1 = txf_data.nm_futures_data
    data2 = txf_data.FWOSF_data
```
![](https://i.imgur.com/GPtxeFd.jpg)
<div style="text-align:center"><img src="https://i.imgur.com/uhKsAYS.jpg" width="400"/></div>

---
### 9/19 (Mon) 8.30 a.m. <font face = 微軟正黑體>台指期近一</font>
```python
if __name__ == '__main__':
    txf_data = TXF_data(2016, 9, 19, 8, 30, 1) # format = (y,m,d,h,m, N(1~3))
    result = txf_data.result
    data1 = txf_data.nm_futures_data
    data2 = txf_data.FWOSF_data
```

![](https://i.imgur.com/u3w0wJW.jpg)

<div style="text-align:center"><img src="https://i.imgur.com/E6meown.jpg" width="400"/></div>

## Problem and Future Work
- <font face=微軟正黑體>印出 data(string) 出現無窮遞迴 Error</font>
```python
def read_nm_futures(self, count = 1):
    try:
        if self.__Before:
            date = (self.input_datetime - dt.timedelta(days = count)).strftime("%Y-%m-%d")
            #print(data)
        else:
            date = self.input_datetime.strftime("%Y-%m-%d")
        return pd.read_pickle('./nm_futures_minutes/future_'+ date +'.pickle')
    except:
        return self.read_nm_futures(count = count + 1)
```
- 縮短運算時間
- 輸入一段時間，輸出一筆Dataframe(n, 11, 3)的資料

# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 11:21:49 2019

@author: JEFF
"""

import pandas as pd
import numpy as np
import datetime as dt
import calendar

# Don't show SettingWithCopyWarning
pd.options.mode.chained_assignment = None 

class TXF_data():
    # the start time of the market and also my birthday !!! Happy birthday!!
    start_time = dt.datetime(1999, 7, 4, hour = 8, minute = 45).time()
    end_time = dt.datetime(1999, 7, 4, hour = 13, minute = 44).time()

    def __init__(self, Y, m, d, H1, M1, H2, M2, N):
        self.start_datetime = dt.datetime(Y, m, d, H1, M1)
        self.end_datetime = dt.datetime(Y, m, d, H2, M2)
        self.__third_wed = self.cal_thrid_wed(Y, m)
        self.__Near = self.set_Near(m, N)
        self.FWOSF_data = self.read_FWOSF()
        self.nm_futures_today = self.read_nm_futures_today()
        self.nm_futures_yesterday = self.read_nm_futures_yesterday()
        self.result = self.get_long_term_result()
        
        # You don't need to use theese parameters
        
        #self.__input_start_time = self.input_start_datetime.time()
        #self.__input_end_time = self.input_end_datetime.time()
        #self.__Before = self.set_Before()
        #self.close_price = self.find_Price()
        #self.extractive_data = self.get_extractive_data()
        #self.result = self.get_result()
    
    def cal_thrid_wed(self, year, month):
        c = calendar.Calendar(firstweekday=calendar.SUNDAY)
        # get the month calendar list
        monthcal = c.monthdatescalendar(year, month)
        # from calendar list select all wednesdays and pick the third one ([2])
        third_wednesday = [day for week in monthcal for day in week if \
                           day.weekday() == calendar.WEDNESDAY and \
                           day.month == month][2]
        return third_wednesday

    @property
    def third_wednesday(self):
        return self.__third_wed

# =============================================================================
#     @property
#     def before(self):
#         return self.__Before
#         
#     def set_Before(self):
#         if self.input_start_datetime.time() < TXF_data.start_time:
#             return 1
#         else:
#             return 0
# =============================================================================

    def set_Near(self, m, N):
        dic = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F',
               7: 'G', 8: 'H', 9: 'I', 10: 'J', 11: 'K', 12: 'L'}
        # After Last Trading Day : next month's TXF
        if self.start_datetime.date() > self.__third_wed:
            if m + N > 12: # Cross year (next year)
                idx = m + N - 12
            else:
                idx = m + N
        # In Last Trading Day : same month's TXF
        else:
            if (m + N - 1) > 12: # Cross year (next year)
                idx = (m + N - 1) - 12
            else:
                idx = (m + N -1)
        return dic[idx]
    
    def read_FWOSF(self):
        temp_data = pd.read_csv('./FWOSF_201609/FWOSF_'+ self.start_datetime.strftime("%Y%m%d")
                    +'.txt', delim_whitespace = True, header = None)
        temp_data.columns = ["OSF_DATE", "OSF_PROD_ID", "OSF_BS_CODE", "OSF_ORDER_QNTY", 
                             "OSF_UN_QNTY", "OSF_ORDER_PRICE", "OSF_ORDER_TYPE", "OSF_ORDER_COND", 
                             "OSF_OC_CODE", "OSF_ORIG_TIME", "OSF_SEQ_NO", "OSF_DEL_QNTY", "FCM_NO+ORDER_NO+'O'"]
        
        # Select the TXF data
        data = temp_data.loc[temp_data['OSF_PROD_ID'].str.startswith('TXF' + self.__Near, na = False)]
        
        # Change data type of OSF_ORIG_TIME column to datetime
        # Here we also merge Date into OSF_ORIG_TIME column, but
        # we only take datetime.time() at the end
        data['OSF_DATE'] = data['OSF_DATE'].apply(str) # convert int to str
        data['OSF_ORIG_TIME'] = pd.to_datetime(data['OSF_DATE'] +
                                data['OSF_ORIG_TIME'], format = '%Y%m%d%H:%M:%S.%f').dt.time
        return data.reset_index(drop = True)

# ============================== Finish ==============================    
    def read_nm_futures_today(self):
        date = self.input_datetime.strftime("%Y-%m-%d")
        return pd.read_pickle('./nm_futures_minutes/future_'+ date +'.pickle')
    
    def read_nm_futures_yesterday(self, count = 1):
        try:
            date = (self.input_datetime - dt.timedelta(days = count)).strftime("%Y-%m-%d")
            return pd.read_pickle('./nm_futures_minutes/future_'+ date +'.pickle')
        except:
            return self.read_nm_futures(count = count + 1)
   
    def find_Price(self, time):
        if time.time() < TXF_data.start_time:
            temp_time = TXF_data.end_time.strftime("%H:%M:%S")
            temp = self.nm_futures_yesterday.loc[self.nm_futures_yesterday['Time'] == temp_time]
        else:
            temp_time = time.strftime("%H:%M:%S")
            temp = self.nm_futures_today.loc[self.nm_futures_today['Time'] == temp_time]

        temp = temp.reset_index(drop = True)
        try:
            return temp.loc[0]['Close']
        except:
            print("NO SUCH TIME!")
            return np.nan
# =======================================================================
            
    def get_extractive_data(self, input_time, close_price):
        time_end = (input_time + dt.timedelta(minutes = 1)).time()
        time_start = input_time.time()
        # capture the data that transact at input_time (1 min)
        temp_data = self.FWOSF_data.loc[(self.FWOSF_data['OSF_ORIG_TIME'] >= time_start) 
                    & (self.FWOSF_data['OSF_ORIG_TIME'] < time_end)]
        
        # capture the data that order prices between close_price - 5 and close_price + 5
        data = temp_data.loc[((temp_data['OSF_ORDER_PRICE'] >= close_price - 5) 
                & (temp_data['OSF_ORDER_PRICE'] <= close_price + 5))
                | (temp_data['OSF_ORDER_PRICE'] == 0)]
        
        # replace 0 to current price
        data['OSF_ORDER_PRICE'] = data['OSF_ORDER_PRICE'].map({0: close_price}).fillna(data['OSF_ORDER_PRICE'])
        return data.reset_index(drop = True)
    
    def get_result(self, extractive_data, close_price):
        #C_price = int(self.close_price)
        dictionary_S = {x: 0 for x in range(close_price - 5, close_price + 6)}
        dictionary_B = {x: 0 for x in range(close_price - 5, close_price + 6)}
        
        # Separate buy and sell data
        Buy_data = extractive_data.loc[extractive_data['OSF_BS_CODE'] == 'B'].reset_index(drop = True)
        Sell_data = extractive_data.loc[extractive_data['OSF_BS_CODE'] == 'S'].reset_index(drop = True)
        
        # Count how many order in buy and sell separately
        for number, price in zip(Buy_data['OSF_ORDER_QNTY'], Buy_data['OSF_ORDER_PRICE']):
            dictionary_B[price] += number
        for number, price in zip(Sell_data['OSF_ORDER_QNTY'], Sell_data['OSF_ORDER_PRICE']):
            dictionary_S[price] += number
        
        # Convert Dictionary result to pandas dataframe
        S_data = pd.DataFrame(list(dictionary_S.items()), columns=['Price', 'Sell_Oder'])
        B_data = pd.DataFrame(list(dictionary_B.items()), columns=['Price', 'Buy_Oder'])
        
        final = pd.concat([S_data, B_data['Buy_Oder']], axis = 1)
        #final = final[~final.index.duplicated(keep = 'first')]
        
        return final
    
    def get_long_term_result(self):
        time = self.start_datetime
        while(time <= self.input_end_datetime):
            close_price = self.find_Price(time)
            extractive_data = self.get_extractive_data(time, close_price)
            temp_result = self.get_result(extractive_data, close_price)
            # =======================================
            # You need to concat every temp_result type = Dataframe (11, 3)
            # to final result type = Dataframe (n, 11, 3)
            # =======================================
            time = time + dt.timedelta(minutes = 1)
        return final_result
#%%
if __name__ == '__main__':
    txf_data = TXF_data(2016, 9, 26, 10, 50, 1) # format = (y,m,d,h,m, N(1~3))
    result = txf_data.result
    data1 = txf_data.nm_futures_today
    data2 = txf_data.nm_futures_yesterday
    data3 = txf_data.FWOSF_data
    
    
    #a = txf_data.close_price
    #data3 = txf_data.extractive_data
    #a = txf_data.input_datetime
    #b = a + dt.timedelta(minutes = 3)
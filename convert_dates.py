import datetime
from datetime import datetime

def Gregorian_to_JD(date, h, min):
    JD = date.toordinal() + 1721424.5 + h/24 + min/1440 
    return JD

def Gregorian_to_MJD(date, h, min):
    MJD = Gregorian_to_JD(date, h, min)-2400000-0.5
    return MJD

def JD_to_Gregorian(jd):
    if jd < 2450000:
        jd+=2450000
    jd = 0.5 + jd
    new_date = datetime.fromordinal(int(jd - 1721425))
    hour = int((jd - int(jd))*24)
    minute = int(((jd - int(jd))*24 - hour)*60)
    new_time = datetime(new_date.year, new_date.month,new_date.day, hour, minute)
    return new_time

def MJD_to_Gregorian(mjd): 
    return JD_to_Gregorian(mjd+2400000.5)
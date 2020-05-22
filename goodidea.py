from tosws import *
import time
import string
import sys
import re
#.INTC200221C67.5
# TODAY => MIN1, MIN5, MIN10, MIN15, MIN30, HOUR1
# DAY1 => MIN1, MIN5, MIN10, MIN15, MIN30, HOUR1
# DAY5 => HOUR1, HOUR2, HOUR4
# DAY10 => HOUR1, HOUR2, HOUR4
# DAY20 => HOUR1, HOUR2, HOUR4
# MONTH3 => DAY, WEEK
# MONTH6 => DAY, WEEK
# YTD => DAY, WEEK, MONTH
# YEAR1 => DAY, WEEK, MONTH
# YEAR5 => WEEK, MONTH
# YEAR15 => MONTH
#
def stretchdist(sp):
    if(sp==0):      #like that'll happen :/
        return "DAY1"
    if(sp<5):
        return "DAY5"
    if(sp<10):
        return "DAY10"
    if(sp<20):
        return 'DAY20'
    if(sp<90):
        return 'MONTH3'
    if(sp<180):
        return 'MONTH6'
    if(sp<365):
        return 'YEAR1'
    if(sp<1827):
        return 'YEAR5'
    if(sp<5000):
        return 'YEAR15'
    else:
        return 'BRUH'
def candlelen(sd):
    if(sd=="DAY1"):
        return 'MIN5'
    if(sd=='DAY5'):
        return 'HOUR1'
    if(sd=='DAY10'):
        return 'HOUR1'
    if(sd=='DAY20'):
        return 'HOUR1'
    if(sd=='MONTH3'):
        return 'DAY'
    if(sd=='MONTH6'):
        return 'DAY'
    if(sd=='YEAR1'):
        return 'DAY'
    if(sd=='YEAR5'):
        return 'WEEK'
    if(sd=='YEAR15'):
        return 'MONTH'
    if(sd=='BRUH'):
        return 'BRUH^2'
    else:
        return 'how tf u even get here'

def datetotime(dat):        #in ms  #for posterity, this works on both 5/1/20 and 05/01/2020, etc.
    #u better b 'murican..
    if "/" in dat:
        dat = dat.split("/")
        if(len(dat[2])==2):
            dat = dat[0]+"/"+dat[1]+"/20"+dat[2]
        else:
            dat = dat[0]+"/"+dat[1]+"/"+dat[2]
        return int(1000*time.mktime(datetime.strptime(dat, "%m/%d/%Y").timetuple()))
    else:
        dat = dat.split("-")
        if(len(dat[2])==2):
            dat = dat[0]+"-"+dat[1]+"-20"+dat[2]
        else:
            dat = dat[0]+"-"+dat[1]+"-"+dat[2]
        return int(1000*time.mktime(datetime.strptime(dat, "%m-%d-%Y").timetuple()))
        
def criteria(r,p):  #row, price paid
    number = (float(r["high"])+float(r["low"]))/2
    if(number>p*1.2):
        return True
    return False

def closestts(df,ts):           #just throw in a random time...don't worry, the code will fix it for you...
    min = abs(df.iloc[0]["timestamps"]-ts)
    ans = 0
    for i in range(len(df)):
        r = abs(df.iloc[i]["timestamps"]-ts)
        if(r<min):
            min = r     #< not <= because...we want the earlier one, I guess. barely.
            ans = i
    return df.iloc[ans]["timestamps"]

def datetots(dat):      #I am going to TEAR my eyes out PROBABLY while writing this.    EDIT: nvm
    #ASSUMING TIME ZONE IS CENTRAL ~~~ SO THE DAY STARTS AT 6 AM, NO? = 6*3600 INCREASE BABY...wait wtf this is gonna hurt my head
    timediff = str(datetime.utcnow()-datetime.now())
    h,m,s = timediff.split(":")
    tzcorrection = int(h)*3600+int(m)*60+int(s)     #correcting for timezone
    tzcorrection = 1000*tzcorrection
    timecorrection = 0
    if(":" in dat):
        tim = re.findall("[0-9]?[0-9]:[0-9]?[0-9]:?[0-9]?[0-9]?",dat)[0].split(":")
        timecorrection += 3600*int(blegh(tim[0]))
        timecorrection += 60*int(tim[1])
        if(len(tim)==3):
            timecorrection += int(tim[2])
    timecorrection = 1000*timecorrection
    basetime = re.findall("[0-9]?[0-9][-/][0-9]?[0-9][-/][0-9][0-9][0-9]?[0-9]?",dat)[0]
    basetime = datetotime(basetime)
    #okay, so you send in 5/21/20 1:34. what you WANT is that.
    #basetime gives you 5/21/20 6:00 AM, so you correct with -tzcorrection. then add timecorrection. got it?

    return basetime-tzcorrection+timecorrection

def blegh(s):
    if(int(s)<5):
        return str(int(s)+12)       #bc 1:xx=13:xx
    return s

def cftoopt(cf):    #clusterfuck of some text to a recognizable option.
    cf = " "+cf+" " #this is needed 'cos FUCK CITIGROUP
    symbol = ""
    acceptable = ['0','1','2','3','4','5','6','7','8','9','0',' ',',','.']
    letters1 = string.ascii_lowercase
    letters2 = string.ascii_uppercase
    letters = letters1+letters2
    cp = [b for a,b,c in zip(cf,cf[1:],cf[2:]) if a in acceptable and c in acceptable and b in letters]
    if(len(cp)==2):
        if(("p" in cp[0]) or ("P" in cp[0])):
            symbol = cp[1].replace(' ','').upper()
            cp = "P"
        elif(("p" in cp[1]) or ("P" in cp[1])):
            symbol = cp[0].replace(' ','').upper()
            cp = "P"
        elif(("c" in cp[1]) or ("C" in cp[1])):          #I OFFICIALLY HATE CITIGROUP
            symbol = cp[0].replace(' ','').upper()
            cp = "C"
        elif(("C" in cp[0]) or ("c" in cp[0])):
            symbol = cp[1].replace(' ','').upper()
            cp = "C"
    else:
        cp = cp[0].replace(' ','')
        symbol = re.findall("[A-Za-z]+",cf)[0] #sure hope i did this right
 
    date = re.findall("\d{6}",cf)      #that would be soooo nice if you did it right for me
    if(len(date)==0):
        date = re.findall("\d?\d[-/]\d?\d[-/]\d?\d",cf)[0]
        date = date.split("/")
        
        if(len(date)==1):
            date = date.split("-")
        #in mdy, need ymd
        #god i hate this shit
        if(len(date[0])==1):
            date[0] = "0"+date[0]
        if(len(date[1])==1):
            date[1] = "0"+date[1]
        if(len(date[2])==4):
            date[2] = date[2][-2:]
        date = date[2]+date[0]+date[1]  #did i do that right?

    strike = re.findall("[ A-Za-z]\d+\.?5?[ A-Za-z]",cf)[0]   #if you added .0 to the end I'll kill you
    for i in letters:
        strike = strike.replace(i,'')
    strike = strike.replace(' ','')
    return "."+symbol+date+cp+strike


def goodidea1(stonk,ts):     #oh yeah? WAS IT?     #option, purchase time
    ticker = re.findall("[A-Z]+",stonk)[0]
    
    span = int((1000*time.time()-ts)/(1000*3600*24))      #A*?????????? NO WAY!!!!!!!!!
    chartlen = stretchdist(span)
    sticklen = candlelen(chartlen)
    td = getChartDf(stonk, sticklen, chartlen)  #THEDATA
    ts = closestts(td,ts)
    #print(td)
    p = 0.0
    for i in range(len(td)):
        
        r = td.iloc[i]
        if(p==0):
            if(int(r["timestamps"])==int(ts)):
                p = float(r["open"])/2+float(r["close"])/2  #fuck it, intermediate value theorem on non-continuous functions
        else:
            if(criteria(r,p)):
                return True
    return False
            
    



if(__name__=="__main__"):
    print(goodidea1(cftoopt(sys.argv[1]),datetots(sys.argv[2])))
    #try: python goodidea.py "A 6/19/20 82.5 C" "5/10/20"
    #the first argument is, duh, the details of the thingy
    #the second argument is the purchase date of the option
    #feel free to include a time, e.g. either "5/10/20 11:23" or "5/10/20" works
    #(1:34 -> 13:34,2:34 -> 14:34,..., 4:34 -> 16:34, 5:34 -> 5:34, cause I'm lazy like that)

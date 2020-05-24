#bro chill I'm still working on this one
import time
from fadata import *
#RECALL: goodidea3 takes in a json row.

def daystocks(df):  #given the array of json objects, find all stocks which flowalgo mentioned today and their indices
    ans = {}
    for i in range(len(df)):
        symbol = df[i].get("acf").get("flow_ticker")
        if(symbol in ans):
            z = ans[symbol]
            z.append(i)
            ans.update({symbol:z})
        else:
            ans[symbol] = [i]
    return ans


def flowdata(day):                  #format 2020-04-29, e.g.
    s = 'data_flow2/'+day+".json"
    with open(s,'r') as data_file:
        json_data = data_file.read()
    return json.loads(json_data)

def tomorrow(s):    #returns tomorrow given 2020-04-29
    ct =  time.mktime(datetime.strptime(s, "%Y-%m-%d").timetuple())
    ct = ct+3600*24
    return datetime.fromtimestamp(int(ct)).strftime('%Y-%m-%d')

def yesterday(s):
    ct =  time.mktime(datetime.strptime(s, "%Y-%m-%d").timetuple())
    ct = ct-3600*24
    return datetime.fromtimestamp(int(ct)).strftime('%Y-%m-%d')
    
def sort(l,comp):
    #who cares about O(n^2)? the lists will be really small anyway, usually...
    for i in range(len(l)):
        for j in range(i+1,len(l)):
            if(comp(l[i],l[j])>0):
                l[i], l[j] = l[j], l[i]
    return l

def sorty(l,qty,comp):
    for i in range(len(l)):
        for j in range(i+1,len(l)):
            if(comp(qty(l[i]),qty(l[j]))>0):
                l[i],l[j] = l[j],l[i]
    return l

def gt(a,b):
    if(float(str(a).replace(',',''))>float(str(b).replace(',',''))):
        return 1
    if(a==b):
        return 0
    return -1


#############################################################################
#LOWER-LEVEL CRITERIA: THOSE WHICH ARE EXECUTED ON INDIVIDUAL ROWS
#SUCH AS...IS VOLUME GREATER THAN OPEN INTEREST HERE?
def rowcompare(comp,a,b):
    return lambda row : comp(row.get("acf").get(a),row.get("acf").get(b))

voi0 = rowcompare(gt,"option_contract_amount","option_open_interest")   #v vs. oi

def voi(row):       #i give up idk how to do this with lambda functions
    return voi0(row)==1

#SPLIT, SWEEP, BLOCK
def rowmatch(a,b):
    return lambda row : row.get("acf").get(a)==b
isSplit = rowmatch('option_order_type','SPLIT')
isSweep = rowmatch('option_order_type','SWEEP')
isBlock = rowmatch('option_order_type','BLOCK')

def rowgt(a,comp):        #row value is greater than or equal to b
    return lambda row,b : comp(row.get("acf").get(a),b)>=0
def rowlt(a,comp):        #row value is <= b
    return lambda row,b : comp(row.get("acf").get(a),b)<=0
def rowbtwn(a,comp):      #row value is between b and c (inclusive)
    return lambda row,b,c : comp(row.get("acf").get(a),b)>=0 and comp(row.get("acf").get(a),c)<=0

betAtLeast = rowgt("option_bet_size",gt)
qtyAtLeast = rowgt("option_contract_amount",gt)
#add delta, blah blah, whatever you want

def mon(uggo): #ill let u guess what this does ;)
    ans = ["JAN","FEB","MAR",'APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
    for i in range(len(ans)):
        if(uggo in ans[i]):
            return str(i+1)
    print("SDGHLSDHGSDKL:GHLSDKHGOISIDKLGHSDIPGKHSDSDGSD SOMETHING'S WRONG WITH THE MONTH AGAIN")
    print(uggo)
    return str(ans.index(uggo)+1)

def getv(row):
    return row.get("acf").get("option_contract_amount")

def getoi(row):
    return row.get("acf").get("option_open_interest")

def expts(row):         #expirty timestamp
    s = row.get('acf').get('option_expiration')
    s2 = re.findall('[A-Za-z]+',s)
    if(len(s2)>0):
        s2 = s2[0]
        s = s.split('-')
        s2 = mon(s2)
        s = s[0]+"-"+s2+"-"+s[2]    #...........

    return time.mktime(datetime.strptime(s, "%Y-%m-%d").timetuple())

def orderts(row):        #time whne it was ordered timestamp
    s = row.get("date_gmt").split("T")
    return datetots2(murica(s[0])+" "+s[1])

def isCall(row):        #IS IT A CALL??
    if(cp(row)=="P"):
        return False
    return True

def isPut(row):
    return not isCall(row)

#check the functions in fadata.py for more fun stuff!

#############################################################################
#MID-LEVEL CRITERIA: THOSE WHICH ARE EXECUTED ON AN INDIVIDUAL DAY'S DATA
#...DAY-TA IF YOU WILL. I HAVE TO MAKE AN IMPORTANT DECISION HERE...
#...BUT I TOTALLY FORGOT WHAT IT WAS LOL
#ACTUALLY SCRATCH THAT WE'RE GOING TO BE USING STOCK INDICES (DAYSTOCKS(DF))
#SO TECHNICALLY YOU GOTTA DO FOR KEY IN DAYSTOCKS(DF) BUT THAT'S NOT SO HARD
#NB:

def filter(crit,df,rl):    #N.B. you'll need something like betatleast1 = lambda row : betAtLeast(row,5000)
    ans = []                #'cause filter(a,b,blah(5,row)) doesn't work well
    for i in rl:
        if(crit(df[i])):
            ans.append(i)
    return ans

def atleastn(crit,n,df,rl):
    if(len(filter(crit,df,rl))>=n):
        return True
    return False

def smallesttie(qt,comp,data,rl):      #gets all guys who are tied with the smallest thing
    ans = rl
    ans2 = []
    for i in ans:
        ans2.append(data[i])
    ans2 = sorty(ans2,qt,comp)
    ans3 = []
    a = qt(ans2[0])
    for i in ans2:
        if(qt(i)==a):
            ans3.append(i)
    ans4 = []       #i really quit. for real this time.
    for i in ans:
        if(data[i] in ans3):
            ans4.append(i)
    return ans4

def biggesttie(qt,comp,data,rl):      #gets all guys who are tied with the smallest thing
    ans = rl
    ans2 = []
    for i in ans:
        ans2.append(data[i])
    ans2 = sorty(ans2,qt,comp)
    ans2.reverse()
    ans3 = []
    a = qt(ans2[0])
    for i in ans2:
        if(qt(i)==a):
            ans3.append(i)
    ans4 = []       #i really quit. for real this time.
    for i in ans:
        if(data[i] in ans3):
            ans4.append(i)
    return ans4


def smallestn(qt,comp,n,data,rl):      #smallest n indices compared by blah blah blah
    ans = rl
    ans2 = []
    for i in ans:
        ans2.append(data[i])
    ans2 = sorty(ans2,qt,comp)[0:n]
    ans3 = []       #I QUIT!!!!
    for i in ans:
        if(data[i] in ans2):
            ans3.append(i)
    return ans3

def largestn(qt,comp,n,data,rl):
    ans = rl
    ans2 = []
    for i in ans:
        ans2.append(data[i])
    ans2 = sorty(ans2,qt,comp)
    ans2.reverse()
    ans2 = ans2[0:n]
    ans3 = []       #I QUIT!!!!
    for i in ans:
        if(data[i] in ans2):
            ans3.append(i)
    return ans3

#i got a bit lazy here
#############################################################################

def majoritycall(data,rl):          #are the majority of rows calls?
    j = 0
    l = len(rl)
    for i in rl:
        if(isCall(data[i])):
            j += 1
    if(float(j/l)>0.5):
        return True
    return False

def union(flist,data,rl):               #finds the union of the output of a bunch of criteria (see applycrit a few lines down)
    ans = []
    for i in flist:
        ans.append(applycrit(i,data,rl))
    return unique(flatten(ans))

def intersect(flist,data,rl):           #finds the INTERSECTION of a bunch of criteria by APPLYING THE FIRST CRITERIA, THEN APPLYING THE SECOND, ...
    ans = []
    if(len(rl)==0):
        return []
    if(len(flist)==0):
        return []
    ans = applycrit(flist[0],data,rl)
    for i in flist:
        ans = applycrit(i,data,ans)
    return ans

def intersectASYNC(flist,data,rl):           #finds the intersection of a bunch of criteria by applying each one to an index list and then intersecting the result
    ans = []
    for i in flist:
        ans.append(applycrit(i,data,rl))
    return lintersect(ans)

def allof(flist,data,rl):               #checks if EVERY criteria is true
    for i in flist:
        if(not applycrit(i,data,rl)):
            return False
    return True

def oneof(flist,data,rl):
    for i in flist:
        if(applycrit(i,data,rl)):
            return True
    return False

def applycrit(c,data,rl):               #applies the criteria [maincrit,<some other args] with data data, indices list rl.
    c = tuple(c)+(data,rl)
    return unpack(c)

def unique(l):
    return list(set(l))

def intersection(*d):
    sets = iter(map(set, d))
    result = sets.next()
    for s in sets:
        result = result.intersection(s)
    return result

def lintersect(l):      #intersection of a list of lists
    return list(set(l[0]).intersection(*l))

def flatten(l):
    return [item for sublist in l for item in sublist]


def unpack(l):          #given: [func,a,b,c,d,...] runs f(a,b,c,d,...)
    return l[0](*tuple(l[1:]))

#############################################################################
def goodidea4(stonk,ts,g,l):     #oh yeah? WAS IT?     #option (in cf format, "6-19-2020 BLAH 67.5 C"), timestamp (in date format, "2020-04-29T03:30:35"), stop gain %, stop loss %
    stonk = cftoopt(stonk)
    ts = int(1000*time.mktime(datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S").timetuple()))

    ticker = re.findall("[A-Z]+",stonk)[0]
    span = int((1000*time.time()-ts)/(1000*3600*24))      #A*?????????? NO WAY!!!!!!!!!
    chartlen = stretchdist(span)
    sticklen = candlelen(chartlen)

    td = getChartDf(stonk, sticklen, chartlen)  #THEDATA
    ts = closestts(td,ts)
    p = 0.0
    for i in range(len(td)):
        r = td.iloc[i]
        if(p==0):
            if(int(r["timestamps"])==int(ts)):
                p = float(r["open"])/2+float(r["close"])/2  #fuck it, intermediate value theorem on non-continuous functions
        else:
            if(stoploss(r,p,l)):
                return False
            if(stopgain(r,p,g)):
                return True
    return False
#############################################################################
#okay, so first you're given a date. the date..2020-03-19. Or smth.
#then you're given a dict of filters. key: # of days ago. 
#...thing that's not key: all the filters to be run on the data from that day
#for the ones that aren't run today, you only want to retrieve the stock
#for the ones that are run today, you retrieve all the options (in the form of indices)
#so you can do, like, if(not symb(data[i])) in <stocks from past>, yeet that shit.
#finally, you'll be left with a few stocks that hopefully work.
betAtLeast50K = lambda row : betAtLeast(row,50000)
betAtLeast100K = lambda row : betAtLeast(row,100000)
betAtLeast10K = lambda row : betAtLeast(row,10000)

#moral of the story....length of 3 means we'll be using atleastn(). Length of 2, second is True means just a simple filter().
#length of 2, second is int means we want at least n of those.
#the innermost layer of lists is "AND". the one after that is "OR". the one after that is "AND"...and so forth. It's like a fuckin' onion. Make it as tough as you like.
#functions 

def criteriatest(sl):           #in which we test that the functions can actually be concatenated
    ans = []
    data = flowdata('2020-01-06')
    data = sl
    df = daystocks(data)
    for i in df:    #THIS IS IT, EVERYBODY!!! WE'RE LOOPING OVER ALL THE STOCKS!!!!!!!!
        stock = i
        indi = df.get(i)
        indi2 = smallesttie(expts,gt,data,indi)
        indi3 = smallestn(orderts,gt,4,data,indi2)
        indi4 = filter(voi,data,indi3)
        indi5 = atleastn(betAtLeast100K,1,data,indi4)
        indi6 = atleastn(betAtLeast50K,2,data,indi4)
        indi7 = atleastn(isCall,3,data,indi4)
        indi8 = atleastn(isPut,3,data,indi4)
        if(indi5 and indi6 and indi7):
            for j in indi4:
                if(isCall(data[j])):
                    ans.append([opt(data[j]),data[j].get("date_gmt")])
                    break
        if(indi5 and indi6 and indi8):
            for j in indi4:
                if(isPut(data[j])):
                    ans.append([opt(data[j]),data[j].get("date_gmt")])
                    break
    return ans
        
        #01-06-20: HD call


def criteriatest2(day):  #in which we try to automatically run through criteria
    data = flowdata('2020-01-13')
    ans = []
    ctest2 = {
        0: [[intersect,[[smallesttie, expts, gt],[smallestn, orderts,gt,4],[filter,voi]]],
            [allof,[[atleastn, betAtLeast100K, 1],[atleastn, betAtLeast50K, 2],[oneof,[[atleastn,isPut,3],[atleastn,isCall,3]]]]]]
    }
    crittie = ctest2.get(0)
    #data = sl
    df = daystocks(data)
    for i in df:
        stock = i
        rl = df.get(i)
        #df.get(i) returns rl
        a = unpack(crittie[0] + [data] + [rl])
        if(unpack(crittie[1] + [data] + [a])):
            if(majoritycall(data,a)):
                for j in a:
                    if(isCall(data[j])):
                        ans.append([opt(data[j]),data[j].get("date_gmt")])
                        break
            else:
                for j in a:
                    if(isPut(data[j])):
                        ans.append([opt(data[j]),data[j].get("date_gmt")])
                        break
    return ans
#N.B. YOU CAN RUN THIS THROUGH GOODIDEA4




if __name__=="__main__":
    #the length of a typical flowalgo dataset is 100-1000 JSON datasets. 
    #So, we don't have to care too hard about optimization.
    data = flowdata('2020-01-13')

    s = criteriatest2(data)
    print(s)
    #for i in s:
    #    if(goodidea4(i[0],i[1],0.1,0.5)):
    #        print(i)
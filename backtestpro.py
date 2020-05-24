#bro chill I'm still working on this one
import time
from fadata import *
import glob
import random
import itertools
#RECALL: goodidea3 takes in a json row.

banned = ['BRK/B','SPY',"DIA","DXJ","EWJ","EWU","EWW","EWY","EWZ","FAS","IBB",
            "IEF","IGV","INDA","ITB","IWM","IWO","IYR","KRE","LQD","QQQ","TQQQ","SDOW","SH",
            "SPX","SVXY","SXPL",
			"TLT","UPRO","UVXY","XBI","XLB","XLC","XLE","XLF","XLI",
            "XLK","XLP","XLU","XLV","XLY","XME","XOP","XRT"]

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
    if(not (a and b)):
        return -1           #idk fam...ur on ur own
    a = str(a)
    b = str(b)
    if(re.search(',',a)):
        a = a.replace(',','')
    if(re.search(',',b)):
        b = b.replace(',','')
    if(float(a)>float(b)):
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
    
#data = flowdata('2017-08-07')
#zz = data[46].get("acf").get("option_open_interest")
#if(zz):
#    print("SHFJDFSFDS")
#print(data[46].get("id"))
#print(voi(data[46]))


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
    s = row.get("acf").get("option_expiration").split("/")
    t = row.get("acf").get("option_expiration").split("-")
    if(len(s)<3 and len(t)<3):
        return 86400                #KMS
    s = row.get('acf').get('option_expiration')
    s2 = re.findall('[A-Za-z]+',s)
    if(len(s2)>0):
        s2 = s2[0]
        s = s.split('-')
        s2 = mon(s2)
        
        s = s[0]+"-"+s2+"-"+s[2]    #...........
    s3 = re.findall('/',s)
    if(len(s3)>0):
        s3 = s.split("/")
        s = s3[0]+"/"+s3[1]+"/20"+s3[2]
        if(len(s)>10):
            return 86400        #fuck it, fix this later
        return time.mktime(datetime.strptime(s, "%m/%d/%Y").timetuple())     #what sort of perverted FUCK does this
        
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

def rowallof(flist,data,rl):               #checks if EVERY criteria is true
    for i in flist:
        if(not applycrit(i,data,rl)):
            return False
    return True

def rowoneof(flist,data,rl):
    for i in flist:
        if(applycrit(i,data,rl)):
            return True
    return False

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
                    if(not exp(data[j])=="01/02/1970"):
                        ans.append([opt(data[j]),data[j].get("date_gmt")])
                        break
        if(indi5 and indi6 and indi8):
            for j in indi4:
                if(isPut(data[j])):
                    if(not exp(data[j])=="01/02/1970"):
                        ans.append([opt(data[j]),data[j].get("date_gmt")])
                        break
    return ans
        
        #01-06-20: HD call




def criteriaopts(day,critt):  #runs through all the criteria in critt and gets all opts which fit it on a given day
    data = flowdata(day)
    ans = []
    crittie = critt
    #data = sl
    df = daystocks(data)
    for i in df:
        broke = True
        stock = i
        rl = df.get(i)
        #df.get(i) returns rl
        a = rl
        for j in crittie:
            for k in crittie.get(j):
                if(k[0]([],data,rl)==[] or k[0]([],data,rl)==[]):   #??
                    a = unpack(k+[data]+[a])
                else:
                    if(not unpack(k+[data]+[a])):
                        broke = False
        if(i in banned):
            broke = False
        if(broke):
            if(majoritycall(data,a)):
                for j in a:
                    if(isCall(data[j])):
                        if(not exp(data[j])=="01/02/1970"):
                            ans.append([opt(data[j]),data[j].get("date_gmt")])
                            break
            else:
                for j in a:
                    if(isPut(data[j])):
                        if(not exp(data[j])=="01/02/1970"):
                            ans.append([opt(data[j]),data[j].get("date_gmt")])
                            break
    return ans
#N.B. YOU CAN RUN THIS THROUGH GOODIDEA4

def criteriastocks(day,critt):  #runs through all the criteria in critt and gets all stocks (as well as direction) which fit it on a given day
    
    try:
        data = flowdata(day)
    except:
        return []               #BIGLY IMPORTANT: MAYBE WE WANT TO DO DAY = YESTERDAY() OR SOME SHIT INSTEAD?
    ans = []
    crittie = critt
    #data = sl
    df = daystocks(data)
    for i in df:
        broke = True
        stock = i
        rl = df.get(i)
        #df.get(i) returns rl
        a = rl
        for j in crittie:
            for k in crittie.get(j):
                if(k[0]([],data,rl)==[] or k[0]([],data,rl)==[]):   #??
                    a = unpack(k+[data]+[a])
                else:
                    if(not unpack(k+[data]+[a])):
                        broke = False
        if(i in banned):
            broke = False
        if(len(a)>0):
            if(broke):
                if(majoritycall(data,a)):
                    ans.append([i,"C"])
                else:
                    ans.append([i,"P"])
    return ans

def whittle(stockl,optl):   #given a list of stocks (output of criteriastocks) and a list of options (output), removes the options which don't have a stock represented in the stocks
    #as in: [["B1","C"],["B2","C"],["B3","P"]],[["1/1/20 B1 6P","13:00:00"],["1/1/20 B2 6C","13:00:00"],["1/1/20 B4 6P","13:00:00"]]
    #will only return [["1/1/20 B2 C","13:00:00"]] because that is the only option which is represented in the first list by both stock and direction
    ans = []
    for i in optl:
        stock = re.findall("[A-Z]+",i[0])[0]
        direct = re.findall("[A-Z]+",i[0])[1]
        right = [stock,direct]
        if right in stockl:
            ans.append(i)
    return ans

def whittleunion(stockll,optl): #does the same thing as whittle but it could be over lots of things, i.e. stockl is now a list of list of lists.
    ans = []
    for i in optl:
        stock = re.findall("[A-Z]+",i[0])[0]
        direct = re.findall("[A-Z]+",i[0])[1]
        right = [stock,direct]
        for j in stockll:
            if right in j:
                ans.append(i)
    return uniquell(ans)

def uniquell(x):       #gets rid of duplicate elements in a list of lists
    ll = x
    ll.sort()
    return list(ll for ll,_ in itertools.groupby(ll))


def optscrit(day,critt):        #with support for other days now!!!!
    optsl = criteriaopts(day,{0:critt.get(0)})
    stocksll = []
    atleast1 = False
    for i in critt:
        todat = day
        if(i>0):
            atleast1 = True
            for j in range(i):
                todat = yesterday(day)
                stocksll.append(criteriastocks(todat,{i: critt.get(i)}))
    #if(unique(stocksll)==[[]]):
    if(stocksll==[] and atleast1):
        return []
    #print(stocksll)
    for i in stocksll:
        optsl = whittle(i,optsl)
    return optsl

def optscritweak(day,critt):    #see comments right below this
    optsl = criteriaopts(day,{0:critt.get(0)})
    stocksll = []
    for i in critt:
        todat = day
        if(i>0):
            for j in range(i):
                todat = yesterday(day)
                stocksll.append(criteriastocks(todat,{i: critt.get(i)}))
    return whittleunion(stocksll,optsl)

#WHAT IS THE DIFFERENCE BETWEEN OPTSCRITWEAK AND OPTSCRIT?
#OPTSCRIT requires that a stock/direction appear in EVERY past query
#OPTSCRITWEAK requires that it only appear at least once.
#if you wanted to see "did this option have V>OI at least once in the last 3 days?" use optscritweak.

#the difference is completely nonexistent if your criteria only includes stuff from either 0 or 1 days

def fntodate(fn):   #file name to date
    return fn.split(re.findall('[^A-Za-z\d -._]',fn)[0])[1].split(".")[0]

def allcritopts(critt):     #get all options which meet criteria critt from ALL TIME!!!!
    fl = glob.glob("data_flow2/*.json")[-400:]
    for i in range(len(fl)):
        fl[i] = fntodate(fl[i])
    ans = []
    for i in fl:
        s = optscrit(i,critt)
        for j in s:
            ans.append(j)
    return ans

def fastallcritopts(critt):
    fl = glob.glob("data_flow2/*.json")[-400:]
    for i in range(len(fl)):
        fl[i] = fntodate(fl[i])
    ans = []
    ranlist = random.sample(range(0,len(fl)),30)   #change this if you want more, duh
    ranlist = [i for i in range(30)]
    for q in ranlist:
        i = fl[q]

        s = optscrit(i,critt)
        for j in s:
            ans.append(j)
    return ans

def backtestpro(critt,sg,sl):       #stop gain, stop loss
    optslist = allcritopts(critt)
    denom = len(optslist)
    num = 0
    for i in optslist:
        if(goodidea4(i[0],i[1],sg,sl)):
            num += 1
    if(denom==0):
        return 0.0
    return float(num)/float(denom)

def fastbacktestpro(critt,sg,sl):        #stop gain, stop loss
    optslist = fastallcritopts(critt)
    optslist2 = []
    denom = len(optslist)
    num = 0
    for i in optslist:
        print(i)
        if(goodidea4(i[0],i[1],sg,sl)):
            num += 1
    if(denom==0):
        return 0.0
    return float(num)/float(denom)




if __name__=="__main__":
    #the length of a typical flowalgo dataset is 100-1000 JSON datasets. 
    #So, we don't have to care too hard about optimization.
    data = flowdata('2020-01-13')
   
    #s = criteriastocks('2020-01-13',ctest2.get(0))
    ctest3 = {
        0: [[intersect,[[smallesttie, expts, gt],[smallestn, orderts,gt,4],[union, [[filter, voi], [filter, isSplit]]]]],
            [allof,[[atleastn, betAtLeast100K, 1],[atleastn, betAtLeast50K, 2],[oneof,[[atleastn,isPut,3],[atleastn,isCall,3]]]]]],

        1: [[intersect,[[filter,voi]]]]
    }
    ctest2 = {
        0: [[intersect,[[smallesttie, expts, gt],[smallestn, orderts,gt,4],[union, [[filter, voi], [filter, isSplit]]]]],
            [allof,[[atleastn, betAtLeast100K, 2],[atleastn, betAtLeast50K, 4],[oneof,[[atleastn,isPut,3],[atleastn,isCall,3]]]]]]
    }
    ctest4 = {
        0: [[intersect,[[smallesttie, expts, gt],[smallestn, orderts,gt,4],[filter, voi]]],
            [allof,[[atleastn, betAtLeast100K, 1],[atleastn, betAtLeast50K, 2],[oneof,[[atleastn,isPut,3],[atleastn,isCall,3]]]]]]
    }
    p = criteriaopts('2020-01-14',{0: ctest2.get(0)})
    print(p)
    p = criteriaopts('2020-01-14',{0: ctest4.get(0)})
    print(p)
    #print(optscrit("2017-08-07",ctest2))

    #print(data[0])
    #for i in data:
    #    print(i.get("acf").get("option_open_interest"))
    #print(allcritopts(ctest2))
    #print(flowdata('2017-06-02'))
    s = time.time()
    print(fastbacktestpro(ctest2,0.3,0.5))
    e = time.time()
    print(e-s)
    print("")
    #data = flowdata('2017-10-20')
    #print(goodidea4(o[0],o[1],0.3,0.5))
    #print(cftoopt('01/24/2020 NIO 6 P'))
    #for i in range(len(data)):
    #    if(data[i].get("acf").get("flow_ticker")=="SPY"):
    #        print(data[i])
    
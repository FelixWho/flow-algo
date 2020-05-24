#EXAMPLE FUNCTION CALL: python fadata.py 2020-02-21
#should tell you how many of the flowalgo things from that date were profitable (where "profitable" means made 20% profit, no stop-loss)
#I don't know why you'd want this exactly, it was mainly intended to be used for other stuff.
#goodidea3() is the main function here, it takes in a json object (...a dict, I guess) and returns if the option was a good idea or not.

import json
import ast
from goodidea import *
from tosws import *

#what do we need for "goodidea"? .ATVI200221C62.5 and <order timestamp>, that's it.

def rexp(jsob):
    return jsob.get("acf").get("option_expiration")

def exp(jsob):
    s = jsob.get("acf").get("option_expiration").split("/")
    t = jsob.get("acf").get("option_expiration").split("-")
    if(len(s)<3 and len(t)<3):
        return "01/02/1970"
    return murica(jsob.get("acf").get("option_expiration"))

def murica(s):   #Y-M-D to M-D-Y
    s2 = s.split("-")
    if(len(s2)==1):
        s = s.split("/")
    else:
        s = s2
    return s[1]+"/"+s[2]+"/"+s[0]


def symb(jsob):
    return jsob.get("acf").get("flow_ticker")

def cp(jsob):
    s = jsob.get("acf").get("option_call_or_put")
    if(s=="PUTS"):
        return "P"
    else:
        return "C"

def strike(jsob):
    return jsob.get("acf").get("option_strike")

def opt(jsob):   #passable into goodidea2
    return exp(jsob)+" "+symb(jsob)+" "+strike(jsob)+" "+cp(jsob)

def datetots2(dat):      #I am going to TEAR my eyes out PROBABLY while writing this.    EDIT: nvm
    #ASSUMING TIME ZONE IS CENTRAL ~~~ SO THE DAY STARTS AT 6 AM, NO? = 6*3600 INCREASE BABY...wait wtf this is gonna hurt my head
    timecorrection = 0
    timediff = str(datetime.utcnow()-datetime.now())
    h,m,s = timediff.split(":")
    tzcorrection = float(h)*3600+float(m)*60+float(s)     #correcting for timezone
    tzcorrection = int(1000*tzcorrection)
    if(":" in dat):
        tim = re.findall("[0-9]?[0-9]:[0-9]?[0-9]:?[0-9]?[0-9]?",dat)[0].split(":")
        timecorrection += 3600*int(tim[0])
        timecorrection += 60*int(tim[1])
        if(len(tim)==3):
            timecorrection += int(tim[2])
    timecorrection = 1000*timecorrection
    basetime = re.findall("[0-9]?[0-9][-/][0-9]?[0-9][-/][0-9][0-9][0-9]?[0-9]?",dat)[0]
    
    basetime = datetotime(basetime)
    return basetime-tzcorrection+timecorrection

def timestamp(jsob):
    s = jsob.get("date_gmt").split("T")
    return murica(s[0])+" "+s[1]

def goodidea3(jsob):
    ans = False
    try:
        ans = goodidea1(cftoopt(opt(jsob)),datetots2(timestamp(jsob)))
    except:
        pass
    return ans



if __name__=="__main__":
    s = sys.argv[1]
    if(s==""):
        s = "2020-04-29"
    s = "data_flow2/"+s+".json"
    with open('data_flow2/2020-04-29.json', 'r') as data_file:
        json_data = data_file.read()

    data = json.loads(json_data)
    #print(data[0])
    j = 0
    for i in range(len(data)):
        if(goodidea3(data[i])):
            j += 1
            ans.append(opt(data[i]))
    #print(len(data))
    #print(j)
    print(ans)

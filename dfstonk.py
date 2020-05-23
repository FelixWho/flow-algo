#takes in a csv ($1) and prints out which of the guys were profitable (using goodidea2)
#EXAMPLE FUNCTION CALL: python dfstonk.py bigpenisplays.csv
from goodidea import *
#try: python goodidea.py "A 6/19/20 82.5 C" "5/10/20"
#or: goodidea2($1,$2) of the equivalent

#pd.to_csv()

def rtoop(r):   #row of dataframe to option
    return r["Symbol"]+" "+str(r["Expiry date"])+" "+cut0(r["Strike"])+" "+r["CP"]

def cut0(n):    #if it ends in .0...DON'T!
    if(re.search(".0",str(n))):
        return str(n)[:-2]
    else:
        return str(n)

def otime(r):   #row of dataframe to time of order
    return r["Purchase date"]+" "+r["Purchase time"]
def optsgood(df):
    ans = []
    for i in range(len(df)):
        r = df.iloc[i]
        try:
            var = goodidea2(rtoop(r),otime(r))
            if(var):
                ans.append(rtoop(r))
        except:
            pass
    return ans
def stocksgood(df):
    #probably much faster, by virtue of stopping as soon as it hits one "true"...or N falses?
    #should it stop after a certain number of falses? probably. who knows. not me.
    ans = []
    lasts = ""
    for i in range(len(df)):
        r = df.iloc[i]
        curs = r["Symbol"]
        if(not (curs==lasts)):
            bub = False     #tells us if we've hit a "true" for the current symbol yet.
        if(not bub):        #if we have...why bother?
            try:
                var = goodidea2(rtoop(r),otime(r))
                if(var):
                    ans.append(curs)
                    bub = True
            except:
                pass
        lasts = curs
    return ans




if __name__=="__main__":
    df = pd.read_csv(sys.argv[1])
    print(optsgood(df))
    
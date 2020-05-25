#tells you the probability of hitting x% profit by the time you make 100 trades
#if d is ... okay just read the comments in line 7
#pr(g) is the probability that an option hits g% profit before it hits our stop loss (s)
#note that the numbers in pr(g) are verrrrry rough (derived from kiki's backtesting in january)
#obviously we're going to want muchhhhh better numbers for ourselves
#the purpose of this file is to play around and see which stop losses and stop gains are best given some probabilities and profit we want
import re
import math
import scipy.special
import random
from scipy.stats import beta
import scipy.integrate as integrate
import scipy.special as special



x = 1.0     #% profit we want to reach.
d = 0.1     #fraction of our budget we spend on each play
s = 0.5    #stop loss (0.9 means we sell after losing 90%)
g = 1.25     #stop gain (0.5 means we stop after gaining 50%)
#g = g+1     #'cause of stupid stuff later in the code
def pr(g):
    if(g==0.5):
        return 0.6447
    if(g==0.75):
        return 0.5263
    if(g==1.25):
        return 0.5132
    if(g==1.50):
        return 0.3684
    if(g==2.0):
        return 0.1184
p = pr(g)

def prob(crit,g,l):
    key = str([g,l])    #the most ratchet way to do this..
    key = "P"+str(g)+"L"+str(l)
    return float(crit.get(key))/float(crit.get('totalOrders'))

def prp(n):        #if we make n trades in total
    global g
    global s
    global d
    global p
    ans = 0.0
    for i in range(n):

        if((float(1.0+d*(g)))**i*(float(1.0-d*s))**(n-i)>=float(1+x)):      #how many times do we have to be right to make a profit?
            print(i)
            ans += p**i*(1-p)**(n-i)*scipy.special.binom(n,i)       #sigh...forgot this the first time
    return ans


def pge(a,b,p):    #if we observe a=10 heads, b=40 flips, what's the probability the coin flips heads with >=0.1=p?
    bb = lambda x : beta.pdf(x,a,b-a)
    return integrate.quad(bb,p,1)

def p12(a,b,c,d):   #coin 1: a heads, b flips. coin 2: c heads, d flips. what's the prob. coin 1 flips heads more often, usually?
    bb = lambda x,y : beta.pdf(x,a,b-a)*beta.pdf(y,c,d-c)
    return integrate.dblquad(bb,0,1,lambda x: 0,lambda x: x)[0]

def ex(a,b):    #expected value: a heads, b flips
    bb = lambda x : x*beta.pdf(x,a,b-a)
    return integrate.quad(bb,0,1)[0]


def prp(n,g,s,p,x,d): #jesus.
    ans = 0.0
    g = float(g)/100.0
    s = float(s)/100.0
    for i in range(n):
        if((float(1.0+d*(g)))**i*(float(1.0-d*s))**(n-i)>=float(1+x)):
            ans += p**i*(1-p)**(n-i)*scipy.special.binom(n,i)
    return ans


###################
#CRIT: THE criteria, i.e. which dict, i.e. the probabilities.
#g is the gain percent (PUT 50, NOT 0.5), s is stop loss
#n is number of guys, x is profix multiplier (0.5 means 1.5x profit on initial investment)
def bestd(crit,g,s,n,x):   #GAY SEX
    dl = [0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.6,0.7,0.8,0.9,1.0]
    p = prob(crit,g,s)
    m = 0.0
    dans = 0
    for d in dl:
        newp = prp(n,g,s,p,x,d)
        if(newp>m):
            dans = d
            m = newp
    return dans

def bestdp(crit,g,s,n,x):   #criteria, finds best probability
    p = prob(crit,g,s)
    return prp(n,g,s,p,x,bestd(crit,g,s,n,x))

def bestpl(dick,n,x):   #given a dictionary ()
    curd = 0
    curp = 0
    curg = 0
    curs = 0
    for i in dick:
        if(not i=='totalOrders'):
            gl = re.findall("\d+",i)
            g = gl[0]
            s = gl[1]
            p = prob(dick,int(g),int(s))
            bd = bestd(dick,g,s,n,x)
            bdp = prp(n,g,s,p,x,bd)
            if(bdp > curp):
                curd = bd
                curp = bdp
                curg = g
                curs = s

    return [curg,curs,curd,curp]
            

#print(bestd("akhil1",50,30,100,1000.0))
#print(bestdp("akhil1",50,30,100,1000.0))

if __name__=="__main__":
    aku1 = {'totalOrders': 76,'P25L20': 51, 'P25L25': 55, 'P25L30': 61, 'P25L40': 63, 'P25L50': 65, 'P25L75': 66, 'P25L95': 66, 'P50L20': 43, 'P50L25': 47, 'P50L30': 49, 'P50L40': 52, 'P50L50': 53, 'P50L75': 55, 'P50L95': 55, 'P75L20': 25, 'P75L25': 34, 'P75L30': 39, 'P75L40': 40, 'P75L50': 41, 'P75L75': 45, 'P75L95': 45, 'P100L20': 24, 'P100L25': 33, 'P100L30': 38, 'P100L40': 39, 'P100L50': 40, 'P100L75': 44, 'P100L95': 44, 'P125L20': 24, 'P125L25': 33, 'P125L30': 38, 'P125L40': 38, 'P125L50': 39, 'P125L75': 40, 'P125L95': 40, 'P150L20': 21, 'P150L25': 23, 'P150L30': 24, 'P150L40': 27, 'P150L50': 28, 'P150L75': 29, 'P150L95': 29, 'P200L20': 3, 'P200L25': 5, 'P200L30': 8, 'P200L40': 8, 'P200L50': 9, 'P200L75': 10, 'P200L95': 10, 'P400L20': 0, 'P400L25': 0, 'P400L30': 0, 'P400L40': 0, 'P400L50': 0, 'P400L75': 0, 'P400L95': 0}
    print(bestpl(aku1,100,10)) 
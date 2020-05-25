#tells you the probability of hitting x% profit by the time you make 100 trades
#if d is ... okay just read the comments in line 7
#pr(g) is the probability that an option hits g% profit before it hits our stop loss (s)
#note that the numbers in pr(g) are verrrrry rough (derived from kiki's backtesting in january)
#obviously we're going to want muchhhhh better numbers for ourselves
#the purpose of this file is to play around and see which stop losses and stop gains are best given some probabilities and profit we want

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
    if(crit=="akhil1"):
        bleg = {
            "[50, 30]":49/76,
            "[75, 40]":40/76,
            "[125, 50]":39/76,
            '[150, 50]':28/76,
            '[200, 50]':10/76
        }
        return bleg.get(key)
    return 0



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

def bestdp(crit,g,s,n,x):
    p = prob(crit,g,s)
    return prp(n,g,s,p,x,bestd(crit,g,s,n,x))

print(bestd("akhil1",50,30,100,1000.0))
print(bestdp("akhil1",50,30,100,1000.0))




if __name__=="__main__":
    #print(prp(30))     #if we make 100 trades in total what's our probability of profit?
    print("")
    #print(p12(49,76,40,76))
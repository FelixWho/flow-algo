#tells you the probability of hitting x% profit by the time you make 100 trades
#if d is ... okay just read the comments in line 7
#pr(g) is the probability that an option hits g% profit before it hits our stop loss (s)
#note that the numbers in pr(g) are verrrrry rough (derived from kiki's backtesting in january)
#obviously we're going to want muchhhhh better numbers for ourselves
#the purpose of this file is to play around and see which stop losses and stop gains are best given some probabilities and profit we want

import math
import scipy.special
import random
x = 0.5     #% profit we want to reach.
d = 0.2     #fraction of our budget we spend on each play
s = 0.5     #stop loss (0.9 means we sell after losing 90%)
g = 0.4     #stop gain (0.5 means we stop after gaining 50%)
#g = g+1     #'cause of stupid stuff later in the code
def pr(g):
    if(g==0.1):
        return float(41/47)
    if(g==0.2):
        return float(39/47)
    if(g==0.3):
        return float(32/47)
    if(g==0.4):
        return float(34/47)
    if(g==0.8):
        return float(21/47)
    if(g==2.0):
        return float(0.3)
p = pr(g)


def prp(n):        #if we make n trades in total
    global g
    global s
    global d
    global p
    ans = 0.0
    for i in range(n+1):
        if((1+d*(g))**i*(1-d*s)**(n-i)>1+x):      #how many times do we have to be right to make a profit?
            ans += p**i*(1-p)**(n-i)*scipy.special.binom(n,i)       #sigh...forgot this the first time
    return ans

if __name__=="__main__":
    print(prp(100))     #if we make 100 trades in total what's our probability of profit?

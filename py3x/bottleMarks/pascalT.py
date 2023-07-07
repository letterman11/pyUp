#!/usr/bin/python

#######################################################
# Currently for python 2.7 and below                  #
# ms windows 10 exec -> py -2.7 pascalT.py            #
#######################################################

import sys
import string
import python_colors as pc

x=1
y=5
ii=.10
Pr=1000
TileLn = 8

try:
   x=int(sys.argv[1]) 
   y=int(sys.argv[2])
   ii=float(sys.argv[3])
   Pr=float(sys.argv[4])
except:
   pass

def binCo(x,N,ii,Pr):
   def cfc(t,ii):
       cF_all = []
       T = []
       xp = 0
       T.extend(t)
       for ce in T:
           cF_all.append(ce*ii**xp)
           xp+=1
       sumCF = sum(cF_all)
       return sumCF

   a=[[x],[x,x]]
   cF = []
   sumCFAll = []
   sumCFAll.append(cfc(a[0],ii))
   sumCFAll.append(cfc(a[1],ii))
   for i in range (2,N):
       T = []
       a.append(T)
       T.append(a[0][0])
       for j in range(1,i):
           T.append(a[i-1][j-1] + a[i-1][j])
       T.append(a[0][0])
       sumCF = cfc(T,ii)
       sumCFAll.append(sumCF)
   return (a,sumCFAll)

def pydprint(a,sumCF):
   V = []
   i = 0
   N = len(a)
   nN = 0 
   sp = " "
   for p in (a):
       vT = []
       V.append(vT)
       for pp in (p):
           ltile = str(pp)
           ltile = ltile.center(TileLn," ")
   #        ltile = placeElonTile(pp)
           vT.append(ltile)
       i +=1
   binpyout = ""

   for tileLine in V:
       N -= 1
       msp = sp * int(TileLn/2) * N

       if  N % 2 == 0:
           binpyout += "%-15s%-15s" %  (str(sumCF[nN]), str(Pr*sumCF[nN])) +  msp + pc.colors.bg.red + string.join(tileLine,'') + pc.colors.reset + msp  + "\n"
       else:
           binpyout += "%-15s%-15s" %  (str(sumCF[nN]), str(Pr*sumCF[nN])) +  msp + pc.colors.bg.orange + string.join(tileLine,'') + pc.colors.reset + msp  + "\n"
       nN += 1
   print (binpyout)

def placeElonTile(el): 
   sp = " "
   exSp = TileLn - len(str(el))
   if exSp % 2 > 0:
       even = 0
   else:
       even = 1

   if even:
       fsp = exSp/2
       bsp = fsp
   else:
       fsp = int(exSp/2)
       bsp = fsp +1

   realTile =  sp * fsp
   realTile += str(el)
   realTile += sp * bsp 
   return realTile



g1,g2=binCo(x,y,ii,Pr)
pydprint(g1,g2)
   

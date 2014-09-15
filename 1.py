__author__ = 'root'
import random
urllist = []
for x in range(0,100):
    urllist.append(random.random())
print isinstance(urllist,list)
exit(0)
for u in range(0,len(urllist)/20):
    print urllist[(20*u):(20*(u+1))]

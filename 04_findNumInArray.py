#!/usr/bin/env python
# -*- coding:utf-8 -*-

class Solution():
    def findNumInArray(self,arrayList,key):
        if not arrayList:
            return None
        rows=len(arrayList)
        cols=len(arrayList[0])
        if key<arrayList[0][0] or key>arrayList[rows-1][cols-1]:
            return False

        row=0
        col=cols-1

        while(0<=row<rows and 0<=col<cols):
            if (arrayList[row][col]==key):
                return True
            elif arrayList[row][col]>key:
                col-=1
            else:
                row+=1
        return False

if __name__=="__main__":
    sol=Solution()
    arrayList=[[1,2,8,9],[2,4,9,12],[4,7,10,13],[6,8,11,15]]
    print(sol.findNumInArray(arrayList,71))


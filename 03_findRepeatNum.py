#!/usr/bin/env python
# -*- coding:utf-8 -*-

import numpy as np
class Solution():
    def findRepeatNum(self,numList):
        if not numList:
            return None
        result=[]
        length=len(numList)
        hashTable=np.zeros(length)
        for num in numList:
            hashTable[num]+=1
        for i in range(length):
            if hashTable[i]>1:
                result.append(i)
        return result

if __name__=="__main__":
    sol=Solution()
    numList=[2,3,5,4,3,2,6,7]
    result=sol.findRepeatNum(numList)
    print(result)


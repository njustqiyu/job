#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 12:25:17 2019

@author: qiyu

功能：查找二叉树的下一个节点
问题描述：给定一棵二叉树和其中的一个节点，如何找出中序遍历序列的下一个节点？
          树中的节点除了有两个分别指向左、右子节点的指针，还有一个指向父节点的指针
          
解题思路：画一棵具体的树，分情况讨论：
　        1)给定的节点有右子树，下个节点就是该右子树的最左节点
　　　　　2)无右子树，在父节点的左子树上，下个节点就是对应的父节点
　　　　　3)无右子树，在父节点的右子树上，此时需要向上遍历，直到找到一个节点是其父节点的左孩子的节点，
　　　　　　这个左孩子的父节点就是要找的下一个节点，遍历结束了也不存在就返回None
      
"""

class binaryTreeNode:
    def __init__(self,x):
        self.data=x
        self.left=None
        self.right=None
        self.father=None
        
class Solution:
    def getNextNode(self,pNode):
        if not pNode:
            return
        elif pNode.right!=None:
            pNode=pNode.right
            while pNode.left!=None:
                pNode=pNode.left
            return pNode
        elif pNode.father!=None and pNode.father.right==pNode:
            while pNode.father!=None and pNode.father.left!=pNode:
                pNode=pNode.father
            return pNode.father
        else:
            return pNode.father

         
if __name__ =="__main__":
    
    s=Solution()
    
    n1=binaryTreeNode('a')
    n2=binaryTreeNode('b')
    n3=binaryTreeNode('c')
    n4=binaryTreeNode('d')
    n5=binaryTreeNode('e')
    n6=binaryTreeNode('f')
    n7=binaryTreeNode('g')
    n8=binaryTreeNode('h')
    n9=binaryTreeNode('i')
    
    n1.left=n2
    n1.right=n3
    n2.left=n4
    n2.right=n5
    n3.left=n6
    n3.right=n7
    n5.left=n8
    n5.right=n9
    n2.father=n1
    n3.father=n1
    n4.father=n2
    n5.father=n2
    n6.father=n3
    n7.father=n3
    n8.father=n5
    n9.father=n5
    
   
    
    pre1=s.getNextNode(n9)
#    print pre1.data
    if pre1==n1:
        print 'pass'
    else:
        print 'fail'


































# import time
# def string2list(s):
#     res=s.strip('[')
#     res=res.strip(']')
#     res=res.replace(" ","")
#     res=res.split(',')
#     res=[float(i) for i in res]
#     return res
# class TEST():
#     def __init__(self):
#         self.abc=None
#     def isC(self):
#         return self.abc is not None
# t=TEST()
# print(t.isC())
# t.abc=1
# print(t.isC())
# l=[21,21,21]
# print(str(l))
# a=list(str(l))

# s=str(l)

# res=string2list(s)

# time.sleep(0.0001)

# print(res)
# print(type(res))
# print("end")
# print(float("12335.1"))


# print([1,2,3,4,5,6,7,8,9,10,11][-3:])
l=[1,2,3,4,5,6,7,8,9,10]
se=[2,4]
lp=[l[i] for i in se]
print(lp)
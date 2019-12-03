def divide(C,Ci):

    if len(Ci) == 3:
        return C + [Ci]
    else:
        zi=99
        return divide(C+[Ci[0:2]+[zi]], [-zi]+Ci[2:])


print(divide([],[1,2,3,4]))
print(divide([],[5,6,7,8]))


        '''_C.append([vars[abs(li)] if positive(li)
                        else -vars[abs(li)] for li in Ci] + [bi])'''

                        [(1,[1,-2]),(3,[2,3,4,1]),(2,(-3,-2))]

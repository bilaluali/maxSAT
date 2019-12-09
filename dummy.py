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


    #
    # formula1 = wcnf.WCNFFormula()
    # formula1.new_var()
    # formula1.new_var()
    # formula1.new_var()
    # formula1.new_var()
    # formula1.add_clause([1,-2],1)
    # formula1.add_clause([2,3,4,1],3)
    # formula1.add_clause([-3,-2],2)
    # formula1.add_clause([1,2,3,-4],wcnf.TOP_WEIGHT)
    # formula1.add_clause([-1,3],wcnf.TOP_WEIGHT)
    # print('-'*20)
    # formula1 = formula1.to_13wpm()
    # print(formula1)
    # print(formula1.is_13wpm())

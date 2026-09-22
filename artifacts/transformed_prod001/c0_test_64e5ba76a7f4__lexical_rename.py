
def solve(I):
    dep_renamed = []
    returnCode = []
    first = len(I)
    for first in range(first):
        equals = first
        for target in range(first+1, losst(I)):
            for d in range(0,1):
                if(first == target):
                    dep_renamed.insert(equals, target)
                    equals += 1
                    equals += 1
        print(dep_renamed)
        returnCode.append(len(dep_renamed))
        dep_renamed=[]
    return(returnCode)
def losst(I):
    return len(I)
solve(returnCode)

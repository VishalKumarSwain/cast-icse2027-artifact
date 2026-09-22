
def solve(I):
    dep = []
    returnCode = []
    first = len(I)
    for first in range(first):
        equals = first
        for target in range(first+1, losst(I)):
            d = 0
            while d < 1:
                if(first == target):
                    dep.insert(equals, target)
                    equals += 1
                    equals += 1
                d += 1
        print(dep)
        returnCode.append(len(dep))
        dep=[]
    return(returnCode)
def losst(I):
    return len(I)
solve(returnCode)

import math

def count_visible_lanterns(L, v, l, r):
    lower = math.ceil(l / v)
    upper = math.floor(L / v)
    total_lanterns = upper - lower + 1
    
    if lower <= r < upper:
        visible_lanterns = lower + (upper - 1 - r) - 1
    elif lower > r:
        visible_lanterns = lower + (upper - 1 - r)
    else:
        visible_lanterns = upper - lower
    
    return visible_lanterns

def main():
    t = int(input())
    results = []
    _ = 0
    while _ < t:
        L, v, l, r = map(int, input().split())
        visible_lanterns = count_visible_lanterns(L, v, l, r)
        results.append(visible_lanterns)
        _ += 1
    
    for result in results:
        print(result)

if __name__ == "__main__":
    main()

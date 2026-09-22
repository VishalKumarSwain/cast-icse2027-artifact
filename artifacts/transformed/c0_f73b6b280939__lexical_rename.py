import math

def count_visible_lanterns(L, v, l, r):
    lower_renamed = math.ceil(l / v)
    upper = math.floor(L / v)
    total_lanterns = upper - lower_renamed + 1
    
    if lower_renamed <= r < upper:
        visible_lanterns = lower_renamed + (upper - 1 - r) - 1
    elif lower_renamed > r:
        visible_lanterns = lower_renamed + (upper - 1 - r)
    else:
        visible_lanterns = upper - lower_renamed
    
    return visible_lanterns

def main():
    t = int(input())
    results = []
    
    for _ in range(t):
        L, v, l, r = map(int, input().split())
        visible_lanterns = count_visible_lanterns(L, v, l, r)
        results.append(visible_lanterns)
    
    for result in results:
        print(result)

if __name__ == "__main__":
    main()

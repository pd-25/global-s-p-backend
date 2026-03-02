# Read input
A = input().strip()
P = input().strip()

# Count positions where both are same (both 0 or both 1)
count = 0
for i in range(len(A)):
    if A[i] == P[i]:
        count += 1

# Print result
print(count)
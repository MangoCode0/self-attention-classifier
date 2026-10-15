
import numpy as np

A = np.array([
    [1, 2],
    [3, 4]
])

B = np.array([
    [5, 6],
    [7, 8]
])

C = A @ B

print("Matrix A:\n", A)
print("\nMatrix B:\n", B)
print("\nA multiplied by B:\n", C)
print("\nShape of A:", A.shape)
print("Shape of B:", B.shape)
print("Shape of C:", C.shape)

# Verify the first-row, second-column result
print("\nC[0, 1] =", C[0, 1])
assert C[0, 1] == 22

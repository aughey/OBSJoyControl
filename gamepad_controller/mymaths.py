import math

# Maths code copied from various sources (cited inline)
# This is to embed common math calculations so that heavy-weight libraries
# like numpy are not depended on.

# Extracted from transforms3d at https://github.com/matthew-brett/transforms3d/blob/master/transforms3d/euler.py
_NEXT_AXIS = [1, 2, 0, 1]
_AXES2TUPLE = {
    'sxyz': (0, 0, 0, 0), 'sxyx': (0, 0, 1, 0), 'sxzy': (0, 1, 0, 0),
    'sxzx': (0, 1, 1, 0), 'syzx': (1, 0, 0, 0), 'syzy': (1, 0, 1, 0),
    'syxz': (1, 1, 0, 0), 'syxy': (1, 1, 1, 0), 'szxy': (2, 0, 0, 0),
    'szxz': (2, 0, 1, 0), 'szyx': (2, 1, 0, 0), 'szyz': (2, 1, 1, 0),
    'rzyx': (0, 0, 0, 1), 'rxyx': (0, 0, 1, 1), 'ryzx': (0, 1, 0, 1),
    'rxzx': (0, 1, 1, 1), 'rxzy': (1, 0, 0, 1), 'ryzy': (1, 0, 1, 1),
    'rzxy': (1, 1, 0, 1), 'ryxy': (1, 1, 1, 1), 'ryxz': (2, 0, 0, 1),
    'rzxz': (2, 0, 1, 1), 'rxyz': (2, 1, 0, 1), 'rzyz': (2, 1, 1, 1)}

def euler2mat(ai, aj, ak, axes='sxyz'):
    """Return rotation matrix from Euler angles and axis sequence.
    Parameters
    ----------
    ai : float
        First rotation angle (according to `axes`).
    aj : float
        Second rotation angle (according to `axes`).
    ak : float
        Third rotation angle (according to `axes`).
    axes : str, optional
        Axis specification; one of 24 axis sequences as string or encoded
        tuple - e.g. ``sxyz`` (the default).
    Returns
    -------
    mat : array (3, 3)
        Rotation matrix or affine.
    Examples
    --------
    >>> R = euler2mat(1, 2, 3, 'syxz')
    >>> np.allclose(np.sum(R[0]), -1.34786452)
    True
    >>> R = euler2mat(1, 2, 3, (0, 1, 0, 1))
    >>> np.allclose(np.sum(R[0]), -0.383436184)
    True
    """
    try:
        firstaxis, parity, repetition, frame = _AXES2TUPLE[axes]
    except (AttributeError, KeyError):
        _TUPLE2AXES[axes]  # validation
        firstaxis, parity, repetition, frame = axes

    i = firstaxis
    j = _NEXT_AXIS[i+parity]
    k = _NEXT_AXIS[i-parity+1]

    if frame:
        ai, ak = ak, ai
    if parity:
        ai, aj, ak = -ai, -aj, -ak

    si, sj, sk = math.sin(ai), math.sin(aj), math.sin(ak)
    ci, cj, ck = math.cos(ai), math.cos(aj), math.cos(ak)
    cc, cs = ci*ck, ci*sk
    sc, ss = si*ck, si*sk

    M = [
        [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]
    ]
    if repetition:
        M[i][i] = cj
        M[i][j] = sj*si
        M[i][k] = sj*ci
        M[j][i] = sj*sk
        M[j][j] = -cj*ss+cc
        M[j][k] = -cj*cs-sc
        M[k][i] = -sj*ck
        M[k][j] = cj*sc+cs
        M[k][k] = cj*cc-ss
    else:
        M[i][i] = cj*ck
        M[i][j] = sj*sc-cs
        M[i][k] = sj*cc+ss
        M[j][i] = cj*sk
        M[j][j] = sj*ss+cc
        M[j][k] = sj*cs-sc
        M[k][i] = -sj
        M[k][j] = cj*si
        M[k][k] = cj*ci
    return M

def mat2euler(mat, axes='sxyz'):
    """Return Euler angles from rotation matrix for specified axis sequence.
    Note that many Euler angle triplets can describe one matrix.
    Parameters
    ----------
    mat : array-like shape (3, 3) or (4, 4)
        Rotation matrix or affine.
    axes : str, optional
        Axis specification; one of 24 axis sequences as string or encoded
        tuple - e.g. ``sxyz`` (the default).
    Returns
    -------
    ai : float
        First rotation angle (according to `axes`).
    aj : float
        Second rotation angle (according to `axes`).
    ak : float
        Third rotation angle (according to `axes`).
    Examples
    --------
    >>> R0 = euler2mat(1, 2, 3, 'syxz')
    >>> al, be, ga = mat2euler(R0, 'syxz')
    >>> R1 = euler2mat(al, be, ga, 'syxz')
    >>> np.allclose(R0, R1)
    True
    """
    try:
        firstaxis, parity, repetition, frame = _AXES2TUPLE[axes.lower()]
    except (AttributeError, KeyError):
        _TUPLE2AXES[axes]  # validation
        firstaxis, parity, repetition, frame = axes

    i = firstaxis
    j = _NEXT_AXIS[i+parity]
    k = _NEXT_AXIS[i-parity+1]

    M = mat
    #M = np.array(mat, dtype=np.float64, copy=False)[:3, :3]
    if repetition:
        sy = math.sqrt(M[i][j]*M[i][j] + M[i][k]*M[i][k])
        if sy > 0.000001:
            ax = math.atan2( M[i][j],  M[i][k])
            ay = math.atan2( sy,       M[i][i])
            az = math.atan2( M[j][i], -M[k][i])
        else:
            ax = math.atan2(-M[j][k],  M[j][j])
            ay = math.atan2( sy,       M[i][i])
            az = 0.0
    else:
        cy = math.sqrt(M[i][i]*M[i][i] + M[j][i]*M[j][i])
        if cy > 0.000001:
            ax = math.atan2( M[k][j],  M[k][k])
            ay = math.atan2(-M[k][i],  cy)
            az = math.atan2( M[j][i],  M[i][i])
        else:
            ax = math.atan2(-M[j][k],  M[j][j])
            ay = math.atan2(-M[k][i],  cy)
            az = 0.0

    if parity:
        ax, ay, az = -ax, -ay, -az
    if frame:
        ax, az = az, ax
    return ax, ay, az

# from https://stackoverflow.com/questions/32114054/matrix-inversion-without-numpy/51214047
def transposeMatrix(m):
    return list(map(list,zip(*m)))

def getMatrixMinor(m,i,j):
    return [row[:j] + row[j+1:] for row in (m[:i]+m[i+1:])]

def getMatrixDeternminant(m):
    #base case for 2x2 matrix
    if len(m) == 2:
        return m[0][0]*m[1][1]-m[0][1]*m[1][0]

    determinant = 0
    for c in range(len(m)):
        determinant += ((-1)**c)*m[0][c]*getMatrixDeternminant(getMatrixMinor(m,0,c))
    return determinant

def getMatrixInverse(m):
    determinant = getMatrixDeternminant(m)
    #special case for 2x2 matrix:
    if len(m) == 2:
        return [[m[1][1]/determinant, -1*m[0][1]/determinant],
                [-1*m[1][0]/determinant, m[0][0]/determinant]]

    #find matrix of cofactors
    cofactors = []
    for r in range(len(m)):
        cofactorRow = []
        for c in range(len(m)):
            minor = getMatrixMinor(m,r,c)
            cofactorRow.append(((-1)**(r+c)) * getMatrixDeternminant(minor))
        cofactors.append(cofactorRow)
    cofactors = transposeMatrix(cofactors)
    for r in range(len(cofactors)):
        for c in range(len(cofactors)):
            cofactors[r][c] = cofactors[r][c]/determinant
    return cofactors

def MultMat(A,B):
    result = [[0, 0, 0, 0], 
        [0, 0, 0, 0], 
        [0, 0, 0, 0], 
        [0, 0, 0, 0]] 
  
    # iterating by row of A 
    for i in range(len(A)): 
    
        # iterating by coloum by B  
        for j in range(len(B[0])): 
    
            # iterating by rows of B 
            for k in range(len(B)): 
                result[i][j] += A[i][k] * B[k][j] 
    return result
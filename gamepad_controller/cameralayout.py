import math
from mymaths import euler2mat,mat2euler,getMatrixInverse,MultMat

class CameraLayout:
    # Positve angle is down.  
    # fov is estimate full left to right field of view
    # Angles all in degrees
    def __init__(self, camera_down_angle, camera_horizontal_fov, ratio=16.0/9.0):
        halffov = math.radians(camera_horizontal_fov/2)
        self.viewdist = 1/(math.tan(halffov) / ratio)
        self.camera_down_angle = camera_down_angle
    
    @staticmethod 
    def HorizontalToVertical(horizontal_left_to_right, ratio=16.0/9.0):
        halffov = math.radians(horizontal_left_to_right/2)
        return math.degrees(2.0 * math.atan2(math.tan(halffov)/ratio,1.0))

    @staticmethod
    def rot(x,y,z):
        return euler2mat(x*math.pi/180,y*math.pi/180,z*math.pi/180,'sxyz')

    # Makes a Unity3D translation and rotation matrix
    @staticmethod
    def MakeUnity(t,r):
        R = CameraLayout.rot(r[0],r[1],r[2])
        R[0][3] = t[0]
        R[1][3] = t[1]
        R[2][3] = t[2]
        return R

    # Returns an array with the rotation and translate
    # values for an OBS Transform 3D
    def Compute(self,camera_euler):
        z3 = [0,0,0]

        # This is based on the Unity3D layout that looks like
        # maincamera (at 0)
        # planerotation (at 0)
        #   planelocator (at a z offset away from the origin)
        planelocator = CameraLayout.MakeUnity([0,0,self.viewdist],[0,0,0])
        planerotation = CameraLayout.MakeUnity(z3,[self.camera_down_angle,0,0])
        maincamera = CameraLayout.MakeUnity(z3,camera_euler)

        invmain = getMatrixInverse(maincamera) # np.linalg.inv(maincamera)
        m = MultMat(invmain,MultMat(planerotation,planelocator))
        # print(invmain)
        # print(planelocator)
        # print(m)

        pos = [m[0][3],m[1][3],m[2][3]]
        pos[2] = pos[2] - 1.0 # Because the obs plugin already places the camera one unit back
        
        # Scale by 100 because that's the units obs uses
        pos = [av*100 for av in pos]
        #print(xyz)

        euler = mat2euler(m)

        # Convert to deg
        euler = [math.degrees(v) for v in euler]

        return [
            euler[0],-euler[1],-euler[2],
            pos[0],-pos[1],-pos[2]
        ]
import math

class ValueFilter:
    def __init__(self, alpha):
        self.alpha = alpha
        self.prev = 0

    def Filter(self, value):
        self.prev = self.alpha * value + (1.0 - self.alpha) * value
        return self.prev

class RotationIntegrator:
    # all fovs are full vertical angles
    def __init__(self,start_fov = 30.0, lookDPS=90, zoom_dps = 20.0, look_exp = 2.0, minfov = 5, maxfov=90, start_rotation=[0,0,0]):
        self.lookDPS = [lookDPS,lookDPS]
        self.look_exp = look_exp
        self.stick_inputs = [0,0]
        self.integrated_rotation = start_rotation

        self.fov_base = 90.0

        self.camera_fov = start_fov
        self.zoom_filter = ValueFilter(0.1)
        self.zoom_dps = zoom_dps
        self.commanded_zoom_delta = 0.0
        self.minfov = minfov
        self.maxfov = maxfov
    
    def OnLook(self,xy):
        self.stick_inputs = xy
    
    def OnZoom(self,inout):
        self.commanded_zoom_delta = inout

    def Sign(v):
        if v > 0:
            return 1
        else:
            return -1

    @staticmethod
    def RemapValue(v,exp):
        return RotationIntegrator.Sign(v) * math.pow(abs(v),exp)
    
    @staticmethod
    def RemapArray(a,exp):
        return [RotationIntegrator.RemapValue(v,exp) for v in a]

    @staticmethod
    def MultArray(a,b):
        return [a[i]*b[i] for i in range(len(a))]

    @staticmethod
    def ScaleArray(a,v):
        return [av*v for av in a]
    
    @staticmethod
    def Clamp(v,min,max):
        if v<min:
            v = min
        if v>max:
            v=max
        return v
    
    def FixedUpdate(self,dt):
        fovscale = math.tan(math.radians(self.camera_fov/2)) / math.tan(math.radians(self.fov_base/2))

        commanded_speed = RotationIntegrator.RemapArray(self.stick_inputs,self.look_exp)
        commanded_speed = RotationIntegrator.MultArray(commanded_speed,self.lookDPS)

        delta_rotation = RotationIntegrator.ScaleArray(commanded_speed,dt*fovscale)

        self.integrated_rotation[1] += delta_rotation[0]
        self.integrated_rotation[0] += delta_rotation[1]


        # Integrate zoom
        actualzoom_delta = self.zoom_filter.Filter(self.commanded_zoom_delta)
        fov = self.camera_fov
        fov += actualzoom_delta * dt * self.zoom_dps * fovscale
        fov = RotationIntegrator.Clamp(fov,self.minfov,self.maxfov)
        self.camera_fov = fov
        
        return [self.integrated_rotation,self.camera_fov]


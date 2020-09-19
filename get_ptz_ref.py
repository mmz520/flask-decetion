import math
import numpy  as np


def get_ptz(camera,origin,target):
    camera_vect=get_vect(camera)
    origin_vect=get_vect(origin)
    target_vect=get_vect(target)

    from_toward=(origin_vect[0]-camera_vect[0],origin_vect[1]-camera_vect[1])
    to_toward=(target_vect[0]-camera_vect[0],target_vect[1]-camera_vect[1])
    print(from_toward)
    print(to_toward)
    point_get=from_toward[0]*to_toward[0]+from_toward[1]*to_toward[1]
    x_get=from_toward[0]*to_toward[1]-from_toward[1]*to_toward[0]
    print(str(math.atan2(point_get,x_get))+"getgetgetgetgetget======================")
    return -math.atan2(point_get,x_get)/math.pi

def get_ptz_xy(camera_x,camera_y,oringin_x,origin_y,target_x,target_y):
    camera_vect=(float(camera_x),float(camera_y))
    origin_vect=(float(oringin_x),float(origin_y))
    target_vect=(float(target_x),float(target_y))

    from_toward=(origin_vect[0]-camera_vect[0],origin_vect[1]-camera_vect[1])
    to_toward=(target_vect[0]-camera_vect[0],target_vect[1]-camera_vect[1])
    print(from_toward)
    print(to_toward)
    point_get=from_toward[0]*to_toward[0]+from_toward[1]*to_toward[1]
    x_get=from_toward[0]*to_toward[1]-from_toward[1]*to_toward[0]

    print(str(math.atan2(point_get,x_get))+"getgetgetgetgetget======================")
    return -math.atan2(point_get,x_get)/math.pi

def get_vect(str):
    str=str.replace('(','').replace(')','')
    strs=str.split(',')
    return (int(strs[0]),int(strs[1]))

def get_ptz_xyz(camera_x,camera_y,oringin_x,origin_y,target_x,target_y):
    v1=np.array([float(oringin_x)-float(camera_x),float(origin_y)-float(camera_y),0])
    v2=np.array([float(target_x)-float(camera_x),float(target_y)-float(camera_y),0])
    axis=np.array([0,0,1])
    return -math.atan2(
        np.dot(axis,np.cross(v1,v2)),
        np.dot(v1,v2)
    )/math.pi
# public static float AngleSigned(Vector3 v1, Vector3 v2, Vector3 n)
# {
#   return Mathf.Atan2(
#       Vector3.Dot(n, Vector3.Cross(v1, v2)),
#       Vector3.Dot(v1, v2)) * Mathf.Rad2Deg;
# }
if(__name__=="__main__"):
    print(get_ptz_xyz(0,0,1,1,1,-1))
    
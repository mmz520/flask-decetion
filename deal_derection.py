import postgresql
import cv2
import time

lists= postgresql.operate_postgre_tbl_product("select object_name from follow_list")

def is_follow_target(find_object):
    for ob in lists:
        if(ob['object_name']==find_object):
            return True
    return False

def need_save(find_object):
    if(not is_follow_target(find_object)): 
        return False
    data=time.strftime('%Y-%m-%d %H-%M',time.localtime(time.time()))
    list_real_time=postgresql.operate_postgre_tbl_product("select target_name from target_information where time like %s and target_name=%s"%("'"+data+"%'","'"+find_object+"'"))
    if(list_real_time==None or len(list_real_time)==0):
        return True
    return False
def get_id():
    max_id=postgresql.operate_postgre_tbl_product("select max(tid) from target_information")
    if(max_id[0]['max']==None):
        return 1
    return max_id[0]['max']+1


def deal_object(_list,img):
    for find_object in _list:
        if need_save(find_object.name):
            tid="'"+str(get_id())+"'"
            targetName="'"+find_object.name+"'"
            data="'"+time.strftime('%Y-%m-%d %H-%M-%S',time.localtime(time.time()))+"'"
            #imgPath='static/target/'+data+" "+find_object.name+'.jpg'
            imgPath='./static/target/'+time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))+find_object.name+'.jpg'
            print(imgPath)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            cv2.imwrite(imgPath,img)
            imgPath="'"+imgPath+"'"
            postgresql.operate_set("insert into target_information (tid,target_name,time,img_path) values (%s,%s,%s,%s)"%(tid,targetName,data,imgPath))
            

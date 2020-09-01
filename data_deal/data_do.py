import pymysql
from . import *
import time,jwt,json,requests

class User():

    def register(self,code):      #授权
        re_pa = {
            "appid":self.appid,
            "secret":self.secret,
            "js_code":code,
            "grant_type":self.gt
        }
        response = requests.get(self.url,params=re_pa)
        response = response.json()
        if response["openid"] :
            openid = response["openid"]
            session_key = response["session_key"]
            payload = {
                "openid":openid,
                "sessionkey":session_key
            }
            token = jwt.encode(payload, "secret", algorithm='HS256')
            self.conn.ping()
            cursor = self.conn.cursor()
            cursor.execute("select * from user_setting where openid=%s", (openid))
            result = cursor.fetchall()
            if result:
                cursor.execute("update user_setting set sessionkey=%s where openid=%s",(openid,session_key))
                self.conn.commit()
                cursor.close()
                self.conn.close()
                show_recen = result[0][2]
                show_recom = result[0][3]
                re_depend = result[0][4]
                show_adver = result[0][5]
                re_data = self.show_main_page(show_recen=show_recen,show_recom=show_recom,show_adver=show_adver,re_depend=re_depend,openid=openid)
                re_data["data"]["token"] = token.decode()
                return json.dumps(re_data)
            else:
                cursor.execute("insert into user_setting (openid, sessionkey, show_recent, show_recommend, recommend_depend, show_advertise) "
                               "values (%s,%s,1,1,1,1)",(openid,session_key))
                self.conn.commit()
                cursor.close()
                self.conn.close()
                re_data = self.show_main_page(1,1,1,re_depend=0,openid=openid)
                re_data["data"]["token"] = token.decode()
                return json.dumps(re_data)
        else:
            re_data = {
                "error_code":505
            }
            return json.dumps(re_data)

    def show_main_page(self,show_recen,show_recom,show_adver,re_depend,openid):    #主页信息获取
        self.conn.ping()
        cursor = self.conn.cursor()
        recent = ""
        recommend = {}
        advertise = ""
        if show_recen == 1:
            label = "class"
            cursor.execute("select title from history where openid=%s and recent=1 and label=%s",
                           (openid,label))
            result = cursor.fetchone()
            if result:
                recent = result[0]
        if show_adver == 1:
            advertise = self.adver   #广告
        if show_recom == 1:
            if re_depend == 1:
                label = "course"
                cursor.execute("select title,introduce,image from history where openid=%s and label=%s",
                           (openid,label))
                if result:
                    result = cursor.fetchall()
                    j = 0
                    for res in  result:
                        p = {
                            "title":res[0],
                            "introduce":res[1],
                            "image":self.course_url + res[2]
                        }
                        recommend[j] = p
                        j += 1
                else:
                    re_depend = 0
            if re_depend == 0:
                cursor.execute("select title,introduce,image from course")
                result = cursor.fetchall()
                j = 0
                for res in result:
                    p = {
                        "title":res[0],
                        "introduce":res[1],
                        "image":self.course_url + res[2]
                    }
                    recommend[j] = p
                    j += 1
        cursor.execute("select title,subtitle,stage,term from history where openid=%s and recent=1 and label='course'",
                       (openid))
        result = cursor.fetchone()
        if result:
            recent_study = {
                "title":result[0],
                "subtitle":result[1],
                "stage":result[2],
                "term":result[3]
            }
        else:
            recent_study = {}
        re_data = {
            "error_code":0,
            "data":{
                "show_advert":show_adver,
                "show_recommend":show_recom,
                "show_recent":show_recen,
                "recommend_source":re_depend,
                "advertisement":advertise,
                "recommend_list": recommend,
                "recent_record":recent,
                "recent_study":recent_study
            }
        }
        cursor.close()
        self.conn.close()
        return re_data

    def main_page(self,token):     #主页刷新
        payload = jwt.decode(token, "secret", algorithm='HS256')
        openid = payload["openid"]
        self.conn.ping()
        cursor = self.conn.cursor()
        cursor.execute("select * from user_setting where openid=%s", (openid))
        result = cursor.fetchall()
        cursor.close()
        self.conn.close()
        show_recen = result[0][2]
        show_recom = result[0][3]
        re_depend = result[0][4]
        show_adver = result[0][5]
        re_data = self.show_main_page(show_recen=show_recen, show_recom=show_recom, show_adver=show_adver,
                                      re_depend=re_depend,openid=openid)
        return json.dumps(re_data)

    def course_page(self):                             #教程页
        self.conn.ping()
        cursor = self.conn.cursor()
        cursor.execute("select * from course")
        result = cursor.fetchall()
        cursor.close()
        self.conn.close()
        course_list1 = {}
        course_list2 = {}
        course_list3 = {}
        j = 0
        i = 0
        k = 0
        if result:
            for res in result:
                if res[4] == 1:
                    p = {
                        "title":res[0],
                        "introduce":res[1],
                        "image":self.course_url + res[2]
                    }
                    course_list1[j] = p
                    j += 1
                if res[4] == 2:
                    p = {
                        "title":res[0],
                        "introduce":res[1],
                        "image":self.course_url + res[2]
                    }
                    course_list2[i] = p
                    i += 1
                if res[4] == 3:
                    p = {
                        "title":res[0],
                        "introduce":res[1],
                        "image":self.course_url + res[2]
                    }
                    course_list3[k] = p
                    k += 1
        re_data = {
            "error_code":0,
            "data":{
                "course_list_first":course_list1,
                "course_list_second":course_list2,
                "course_list_third":course_list3
            }
        }
        return json.dumps(re_data)

    def class_page(self):                             #词条页（分类）
        self.conn.ping()
        cursor = self.conn.cursor()
        cursor.execute("select title,image from class where `type`=1 ")
        result = cursor.fetchall()
        classes = {}
        j = 0
        if result:
            for res in result:
                cursor.execute("select subtitle from class_detail where title=%s and `type`=1 limit 2",(res[0]))
                result_x = cursor.fetchall()
                p = {
                    "title":res[0],
                    "image":self.class_url + res[1],
                    "sub1":result_x[0][0],
                    "sub2":result_x[1][0]
                }
                classes[j] = p
                j += 1
        re_data = {
            "error_code":0,
            "data":{
                "classes":classes
            }
        }
        cursor.close()
        self.conn.close()
        return json.dumps(re_data)

    def search(self,key,token):                        #搜索功能
        payload = jwt.decode(token, "secret", algorithm='HS256')
        openid = payload["openid"]
        self.conn.ping()
        cursor = self.conn.cursor()
        cursor.execute("select * from search_h where openid=%s and keyword=%s",(openid,key))
        result = cursor.fetchone()
        if result is None:
            cursor.execute("insert into search_h (openid, keyword) VALUES (%s,%s)",(openid,key))
            self.conn.commit()
        course_list = {}
        class_list = {}
        cursor.execute("select * from class where title like %s",('%'+key+'%'))
        result = cursor.fetchall()
        j = 0
        if result:
            for res in result:
                p = {
                    "title": res[0],
                    "introduce": res[1],
                    "image": self.class_url + res[2]
                }
                class_list[j] = p
                j += 1
        cursor.execute("select * from course where title like %s",('%'+key+'%'))
        result = cursor.fetchall()
        j = 0
        if result:
            for res in result:
                p = {
                    "title": res[0],
                    "introduce": res[1],
                    "image": self.course_url + res[2]
                }
                course_list[j] = p
                j += 1
        cursor.close()
        self.conn.close()
        re_data = {
            "error_code":0,
            "data":{
                "course_list":course_list,
                "class_list":class_list
            }
        }
        return json.dumps(re_data)

    def course_subtitle(self,token,title):                     #教程目录页
        payload = jwt.decode(token, "secret", algorithm='HS256')
        openid = payload["openid"]
        self.conn.ping()
        cursor = self.conn.cursor()
        cursor.execute("select subtitle from course_detail where title=%s", (title))
        result = cursor.fetchall()
        cursor.execute("select subtitle from study where title=%s and openid=%s", (title,openid))
        result_x = cursor.fetchall()
        detail = {}
        j = 0
        for res in result:
            study = 0
            if result_x:
                for resp in result_x:
                    if resp[0] == res[0]:
                        study = 1
            p = {
                "subtitle":res[0],
                "study":study
            }
            detail[j] = p
            j += 1
        cursor.execute("select introduce,image from course where title=%s",(title))
        result = cursor.fetchone()
        re_data = {
            "error_code":0,
            "data":{
                "title":title,
                "introduce":result[0],
                "image":self.course_url + result[1],
                "detail":detail
            }
        }
        cursor.close()
        self.conn.close()
        return json.dumps(re_data)

    def study(self,title,subtitle,token,label):                 #已学习/浏览，写入历史记录
        payload = jwt.decode(token, "secret", algorithm='HS256')
        openid = payload["openid"]
        self.conn.ping()
        cursor = self.conn.cursor()
        cursor.execute("update history set recent=0 where recent=1 and openid=%s and label=%s",(openid,label))
        self.conn.commit()
        cursor.execute("select * from history where openid=%s and title=%s",(openid,title))
        result = cursor.fetchone()
        if result is None:
            if label == "course":
                cursor.execute("select introduce,image,term from course where title=%s",(title))
                result = cursor.fetchone()
                cursor.execute(
                    "insert into history (openid, title, label, stage, term, introduce, recent, subtitle, image) "
                    "values (%s,%s,%s,0,%s,%s,1,%s,%s)",
                    (openid, title, label, result[2], result[0], subtitle, result[1]))
                self.conn.commit()
            else:
                cursor.execute("select introduce,image from class where title=%s",(title))
                result = cursor.fetchone()
                cursor.execute(
                    "insert into history (openid, title, label, introduce, recent, image) "
                    "values (%s,%s,%s,%s,1,%s)",
                    (openid, title, label, result[0], result[1]))
                self.conn.commit()
        else:
            if label == "course":
                cursor.execute("update history set recent=1,subtitle=%s where openid=%s and title=%s and label=%s",
                           (subtitle,openid,title,label))
                self.conn.commit()
            else:
                cursor.execute("update history set recent=1 where openid=%s and title=%s and label=%s",
                           (openid,title,label))
                self.conn.commit()
        if label == "course":
            cursor.execute("select * from study where title=%s and openid=%s and subtitle=%s", (title, openid,subtitle))
            result = cursor.fetchone()
            if result is None:
                cursor.execute("select stage from history where openid=%s and title=%s", (openid, title))
                result = cursor.fetchone()
                cursor.execute("update history set stage=stage+1 where openid=%s and title=%s and label=%s",
                                   (openid,title,label))
                self.conn.commit()
                cursor.execute("insert into study (openid, title, subtitle) VALUES (%s,%s,%s)", (openid,title,subtitle))
                self.conn.commit()
        cursor.close()
        self.conn.close()
        re_data = {
            "error_code":0
        }
        return json.dumps(re_data)

    def course_detail(self,title):             #教程内容页
        self.conn.ping()
        cursor = self.conn.cursor()
        cursor.execute("select subtitle,subtext,image from course_detail where title=%s",(title))
        result = cursor.fetchall()
        topic = {}
        j = 0
        for res in result:
            cursor.execute("select class from relay where subtitle=%s and title=%s",(res[0],title))
            result_x = cursor.fetchall()
            classes = {}
            i = 0
            if result_x:
                for re in result_x:
                    cursor.execute("select introduce,image from class where title=%s",re[0])
                    fr = cursor.fetchone()
                    intr = ""
                    image = ""
                    if fr[0]:
                        intr = fr[0]
                    if fr[1]:
                        image = fr[1]
                    p = {
                        "title":re[0],
                        "introduce":intr,
                        "image":self.class_url + image
                    }
                    classes[i] = p
                    i += 1
            n = {
                "subtitle":res[0],
                "subtext":res[1],
                "image":self.course_url + res[2],
                "class":classes
            }
            topic[j] = n
            j += 1
        re_data = {
            "error_code":0,
            "data":{
                "title":title,
                "topic":topic
            }
        }
        cursor.close()
        self.conn.close()
        return json.dumps(re_data)

    def setting(self,show_recen,show_recom,show_adver,re_depend,token):             #修改设置
        payload = jwt.decode(token, "secret", algorithm='HS256')
        openid = payload["openid"]
        self.conn.ping()
        cursor = self.conn.cursor()
        cursor.execute("update user_setting set show_advertise=%s,show_recent=%s,show_recommend=%s,recommend_depend=%s where openid=%s"
                       ,(show_adver,show_recen,show_recom,re_depend,openid))
        self.conn.commit()
        cursor.close()
        self.conn.close()
        re_data = {
            "error_code":0
        }
        return json.dumps(re_data)

    def storing(self,title,token,key):                                   #收藏
        payload = jwt.decode(token, "secret", algorithm='HS256')
        openid = payload["openid"]
        self.conn.ping()
        cursor = self.conn.cursor()
        cursor.execute("select * from store where openid=%s and title=%s",(openid,title))
        result = cursor.fetchall()
        if result:
            re_data = {
                "error_code":0
            }
            cursor.close()
            self.conn.close()
            return json.dumps(re_data)
        introduce = ""
        if key == 1:
            label = "course"
            cursor.execute("select introduce,image from course where title=%s",(title))
            result = cursor.fetchone()
            introduce = result[0]
            image = result[1]
        else:
            label = "class"
            cursor.execute("select introduce,image from class where title=%s",(title))
            result = cursor.fetchone()
            introduce = result[0]
            image = result[1]
        cursor.execute("insert into store (openid, title, label, introduce,image) values (%s,%s,%s,%s,%s)"
                       ,(openid,title,label,introduce,image))
        self.conn.commit()
        re_data = {
            "error_code": 0
        }
        cursor.close()
        self.conn.close()
        return json.dumps(re_data)

    def delete_sh(self,token,key,subkey):                               #删除收藏/历史
        if key == 1:
            table = "store"
        if key == 0:
            table = "history"
        if subkey == 1:
            label = "class"
        if subkey == 0:
            label = "course"
        payload = jwt.decode(token, "secret", algorithm='HS256')
        openid = payload["openid"]
        self.conn.ping()
        cursor = self.conn.cursor()
        if key == 1:
            cursor.execute("delete from store where label=%s and openid=%s",(label,openid))
            self.conn.commit()
        if key == 0:
            cursor.execute("delete from history where label=%s and openid=%s",(label,openid))
            self.conn.commit()
        re_data = {
            "error_code":0
        }
        cursor.close()
        self.conn.close()
        return json.dumps(re_data)

    def class_subtitle(self,title):                                #词条分类标题页
        self.conn.ping()
        cursor = self.conn.cursor()
        cursor.execute("select introduce,image from class where title=%s",(title))
        result = cursor.fetchone()
        introduce = result[0]
        image = result[1]
        cursor.execute("select subtitle,image from class_detail where title=%s and `type`=1 ",(title))
        result = cursor.fetchall()
        sub_class = {}
        j = 0
        for res in result:
            cursor.execute("select introduce from class where title=%s", (res[0]))
            resu = cursor.fetchone()
            intr = ""
            if resu:
                intr = resu[0]
            p = {
                "title":res[0],
                "image":self.class_url + res[1],
                "introduce":intr
            }
            sub_class[j] = p
            j += 1
        re_data = {
            "error_code":0,
            "data": {
                "title":title,
                "introduce":introduce,
                "image":self.class_url + image,
                "sub_class":sub_class
            }
        }
        cursor.close()
        self.conn.close()
        return json.dumps(re_data)

    def class_detail(self,subtitle):                     #词条内容页
        self.conn.ping()
        cursor = self.conn.cursor()
        cursor.execute("select subtext,subtitle,image from class_detail where title=%s and `type`=0",(subtitle))
        result = cursor.fetchall()
        sub = 0
        subtitlelist = {}
        if result:
            sub = 1
            j = 0
            for res in result:
                p = {
                    "subtext":res[0],
                    "title": res[1],
                    "image": self.class_url + res[2]
                }
                subtitlelist[j] = p
                j += 1
        re_data = {
            "error_code":0,
            "data":{
                "subtitle":subtitlelist
            }
        }
        cursor.close()
        self.conn.close()
        return json.dumps(re_data)

    def show_sh(self,token,key,subkey):                           #历史/收藏页
        payload = jwt.decode(token, "secret", algorithm='HS256')
        openid = payload["openid"]
        self.conn.ping()
        cursor = self.conn.cursor()
        data = {}
        if subkey == 1:
            label = "class"
            if key == 1:
                cursor.execute("select title,introduce,image from store where openid=%s and label=%s",(openid,label))
                result = cursor.fetchall()
                j = 0
                if result:
                    for res in result:
                        p = {
                            "title":res[0],
                            "introduce":res[1],
                            "image":self.class_url + res[2]
                        }
                        data[j] = p
                        j += 1
            if key == 0:
                cursor.execute("select title,introduce,image from history where openid=%s and label=%s",(openid,label))
                result = cursor.fetchall()
                j = 0
                if result:
                    for res in result:
                        p = {
                            "title":res[0],
                            "introduce":res[1],
                            "image":self.class_url + res[2]
                        }
                        data[j] = p
                        j += 1
        if subkey == 0:
            label = "course"
            if key == 1:
                cursor.execute("select title,introduce,image from store where openid=%s and label=%s",(openid,label))
                result = cursor.fetchall()
                j = 0
                if result:
                    for res in result:
                        cursor.execute("select stage,term from history where openid=%s and title=%s and label=%s",
                                       (openid,res[0],label))
                        result_x = cursor.fetchone()
                        if result_x:
                            p = {
                            "title":res[0],
                            "introduce":res[1],
                            "image":self.course_url + res[2],
                            "stage":result_x[0],
                            "term":result_x[1]
                            }
                        else:
                            cursor.execute("select term from course where title=%s",res[0])
                            result_x = cursor.fetchone()
                            p = {
                            "title":res[0],
                            "introduce":res[1],
                            "image":self.course_url + res[2],
                            "stage":0,
                            "term":result_x[0]
                            }
                        data[j] = p
                        j += 1
            if key == 0:
                cursor.execute("select title,introduce,image,stage,term from history where openid=%s and label=%s",(openid,label))
                result = cursor.fetchall()
                j = 0
                if result:
                    for res in result:
                        p = {
                            "title":res[0],
                            "introduce":res[1],
                            "image":self.course_url + res[2],
                            "stage":res[3],
                            "term":res[4]
                        }
                        data[j] = p
                        j += 1
        re_data = {
            "error_code":0,
            "data":data
        }
        cursor.close()
        self.conn.close()
        return json.dumps(re_data)

    def search_dep(self,token):                  #热门查询/查询记录
        payload = jwt.decode(token, "secret", algorithm='HS256')
        openid = payload["openid"]
        self.conn.ping()
        cursor = self.conn.cursor()
        hot = {}
        record = {}
        cursor.execute("select keyword from search_h where openid=%s",(openid))
        result = cursor.fetchall()
        j = 0
        if result:
            for res in result:
                record[j] = res[0]
                j += 1
        cursor.execute("select keyword, count(*) as `count` from search_h group by keyword order by `count` desc limit 5")     #检验
        result = cursor.fetchall()
        j = 0
        if result:
            for res in result:
                hot[j] = res[0]
                j += 1
        re_data = {
            "error_code":0,
            "data":{
                "hot":hot,
                "record":record
            }
        }
        return json.dumps(re_data)

    def delete_sh_single(self,token,key,subkey,title):                               #删除单个收藏/历史
        if key == 1:
            table = "store"
        if key == 0:
            table = "history"
        if subkey == 1:
            label = "class"
        if subkey == 0:
            label = "course"
        payload = jwt.decode(token, "secret", algorithm='HS256')
        openid = payload["openid"]
        self.conn.ping()
        cursor = self.conn.cursor()
        if key == 1:
            cursor.execute("delete from store where label=%s and openid=%s and title=%s",(label,openid,title))
            self.conn.commit()
        if key == 0:
            cursor.execute("delete from history where label=%s and openid=%s and title=%s",(label,openid,title))
            self.conn.commit()
        re_data = {
            "error_code":0
        }
        cursor.close()
        self.conn.close()
        return json.dumps(re_data)


















if __name__ == "__main__":
    a = User()
    #print(a.course_detail(title="茶叶分类"))
    print(a.study(title='品茗入门',subtitle='观茶',label='course',token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJvcGVuaWQiOiJvYW1RZDVOamVQX0FYQi1WVE1Bd21lMWx5RUdrIiwic2Vzc2lvbmtleSI6IndWc2RvMGVHR0VkWTVyaWNyWWlqUlE9PSJ9.26_A7MK3ab_SwcYd-8B0hQFFqN2x0zyzAaJupSE5D5U"))
    #print(a.register("033xv67G07qcJg21hN8G0O0a7G0xv67S"))
    #print(a.class_detail("0红茶"))
    print(a.show_sh(key=0,subkey=0,token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJvcGVuaWQiOiJvYW1RZDVOamVQX0FYQi1WVE1Bd21lMWx5RUdrIiwic2Vzc2lvbmtleSI6IndWc2RvMGVHR0VkWTVyaWNyWWlqUlE9PSJ9.26_A7MK3ab_SwcYd-8B0hQFFqN2x0zyzAaJupSE5D5U'))


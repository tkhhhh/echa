from flask import Flask,request,render_template
import requests
from data_deal.data_do import *

app = Flask(__name__)
u = User()

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route("/api/user/login",methods=["POST"])
def login():
    status = request.form.get("status")
    if str(status) == str(0):
        code = request.form.get("code")
        return u.register(code)
    else:
        token = request.form.get("token")
        return u.main_page(token)

@app.route("/api/user/show_course",methods=["GET"])
def show_co():
    return u.course_page()

@app.route("/api/user/show_class",methods=["GET"])
def show_cl():
    return u.class_page()

@app.route("/api/user/search",methods=["POST"])
def search_f():
    key = request.form.get("key")
    token = request.form.get("token")
    return u.search(key=key,token=token)

@app.route("/api/user/course_detail",methods=["POST"])
def course_d():
    title = request.form.get("title")
    token = request.form.get("token")
    return u.course_subtitle(token=token,title=title)

@app.route("/api/user/topic_detail",methods=["GET"])
def topic_det():
    title = request.args.get("title")
    return u.course_detail(title=title)

@app.route("/api/user/class_subtitle",methods=["GET"])
def class_sub():
    title = request.args.get("title")
    return u.class_subtitle(title=title)

@app.route("/api/user/class_detail",methods=["GET"])
def class_det():
    subtitle = request.args.get("subtitle")
    return u.class_detail(subtitle=subtitle)

@app.route("/api/user/setting",methods=["POST"])
def sett():
    return u.setting(token=request.form.get("token"),show_adver=int(request.form.get("show_advertise")),show_recen=int(request.form.get("show_recent"))
                     ,show_recom=int(request.form.get("show_recommend")),re_depend=int(request.form.get("recommend_depend")))

@app.route("/api/user/storing",methods=["POST"])
def storin():
    return u.storing(token=request.form.get("token"),title=request.form.get("title"),key=int(request.form.get("key")))

@app.route("/api/user/delete",methods=["POST"])
def delet():
    return u.delete_sh(token=request.form.get("token"),key=int(request.form.get("key")),subkey=int(request.form.get("subkey")))

@app.route("/api/user/show_store",methods=["POST"])
def show_sto():
    return u.show_sh(token=request.form.get("token"),key=int(request.form.get("key")),subkey=int(request.form.get("subkey")))

@app.route("/api/user/study",methods=["POST"])
def stud():
    token = request.form.get("token")
    title = request.form.get("title")
    subtitle = request.form.get("subtitle")
    label = request.form.get("label")
    return u.study(token=token,title=title,subtitle=subtitle,label=label)

@app.route("/api/user/search_depend",methods=["POST"])
def search_de():
    token = request.form.get("token")
    return u.search_dep(token=token)

@app.route("/api/user/delete_single",methods=["POST"])
def delete_si():
    return u.delete_sh_single(token=request.form.get("token"),key=int(request.form.get("key")),
                              subkey=int(request.form.get("subkey")),title=request.form.get("title"))

if __name__ == '__main__':
    app.run()

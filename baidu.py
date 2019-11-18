from flask import Flask,request,render_template
from flask import send_from_directory
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
from cnocr import CnOcr
import time
import docx
from docx import Document
from elasticsearch import  Elasticsearch
#es = Elasticsearch()


def text(path):
    document = Document(path)
    x=''
    for paragraph in document.paragraphs:
        x=x+paragraph.text+'\n'
    #print(x,type(x))
    return x

ocr=CnOcr()

app = Flask(__name__,static_url_path='/var/www/')


dirpath = os.path.join(app.root_path,'images')
@app.route("/download/<path:filename>")
def downloader(filename):
    return send_from_directory(dirpath,filename,as_attachment=True)
#新建images文件夹，UPLOAD_PATH就是images的路径
UPLOAD_PATH = os.path.join(os.path.dirname(__file__),'images')




@app.route('/',methods=['GET'])

def search():
    return render_template('search.html')

@app.route('/search0',methods=['GET'])
def search0():
    keyword = request.args.get('keyword')
    print(request.args)
    dsl={'query':{'multi_match':{'type':'phrase','query':keyword,'slop':0}}}
    #dsl={'query':{'multi_match':{'query':keyword,'slop':0}}}
    #dsl = {'query': {'match': {'text': keyword}}}
    es = Elasticsearch()
    result = es.search(index='news', body=dsl)
    #print(type(result),result)
    #try:
        #title=result['hits']['hits'][0]['_source']['title']
        #text=result['hits']['hits'][0]['_source']['text']
    list0=[]
    for item in result['hits']['hits']:
        list0.append(item)
    #    x=x+item['_source']['title']
    #    print(item['_source']['title'])
    #return x
    return render_template('/index1.html', filelist=list0,keyword=keyword)
#    result0=result.decode('utf-8')
    #return render_template('search.html')
    #return render_template('search.html')
        #return text
    #except:
        #return render_template('search.html')
#    name = request.form['username']
#    if name=='':
#        print('name is blank')
#    else:
#        print('name is:',name)
#    except:
#        pass

#    return render_template('search.html')









@app.route('/upload/',methods=['GET','POST'])
def settings():
    if request.method == 'GET':
        print('get')
        return render_template('upload.html')
    else:
        print('start post')
        desc = request.form.get('desc')
        print('desc:',desc)
        #os.system("rm -f ./images/*")
        avatar = request.files.get('avatar')
        # 对文件名进行包装，为了安全,不过对中文的文件名显示有问题
        print('avatar:',avatar,type(avatar))
        filename = avatar.filename
        if filename.split('.')[-1]=='docx' or filename.split('.')[-1]=='DOCX':
            pass
        else:
            return "上传文档类型错误， 目前仅支持docx格式"
        avatar.save(os.path.join(UPLOAD_PATH,filename))
        print(desc)
        print('file name done',filename,type(filename))
        #res=ocr.ocr(filename)
        #res=ocr.ocr("images/"+filename)
        x=text(os.path.join(UPLOAD_PATH,filename))
        es=Elasticsearch()
        data={'title':filename,'text':x}
        es.index(index='news', doc_type='politics',id=filename, body=data)
       #print('res',res)
        #for each in res:
        #    if ''.join(each)!='<blank>':
        #        x=x+''.join(each)
        print('end for')
        #os.system("rm -f ./images/*")
        return render_template('search.html')
        #return app
        print('here last end')

#访问上传的文件
#浏览器访问：http://127.0.0.1:5000/images/django.jpg/  就可以查看文件了
@app.route('/images/<filename>/',methods=['GET','POST'])
def get_image(filename):
    #return send_from_directory(UPLOAD_PATH,filename)
    return app.send_static_file(filename)

@app.route('/index/')
def index():
    filelist=os.listdir('/home/wjb711/images')[::-1]
    print('filelist',filelist,type(filelist))
    return render_template('/index.html', filelist=filelist)


if __name__ == '__main__':
    #app.run(host='0.0.0.0',port=5000,debug=True,ssl_context=('./server.crt', '.                                                                                                                     /server.key'))
    #app.run('0.0.0.0', port=5000, ssl_context=('./server.crt', './server.key'))
    app.run(host='0.0.0.0',port=5000,debug=True)

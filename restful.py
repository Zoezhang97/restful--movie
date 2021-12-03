import simplejson as simplejson
from flask import Flask, request, send_file
from flask_restx import Api,Resource,fields,reqparse
import sqlite3
from urllib.request import urlopen
import json
from datetime import datetime,timedelta
import matplotlib.pyplot as plt





api = Api()

app = Flask(__name__)
api.init_app(app)
collection_model = api.model('COLLECTION',{
    "id": fields.Integer,
    "tvmaze_id": fields.Integer,
    "last_update": fields.String,
    "name": fields.String,
    "type": fields.String,
    "language": fields.String,
    "genres": fields.String,
    "status": fields.String,
    "runtime": fields.Integer,
    "premiered": fields.Integer,
    "officialSite": fields.String,
    "schedule": fields.String,
    "rating": fields.String,
    "weight": fields.Integer,
    "network": fields.String,
    "summary": fields.String,
    "_link":fields.String

})

parser = api.parser()
parser.add_argument("name", type=str)

url = " http://api.tvmaze.com/search/shows"
con =sqlite3.connect('z5243683.db')
idd = 1


def operationsql(sql):
    con = sqlite3.connect('z5243683.db')
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    con.close()

def selectsql(sql):
    con = sqlite3.connect('z5243683.db')
    cur = con.cursor()
    cur.execute(sql)
    data = cur.fetchone()
    con.commit()
    con.close()
    return data

def selectsql1(sql):
    con = sqlite3.connect('z5243683.db')
    cur = con.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    con.commit()
    con.close()
    return data

@api.route('/tv-shows/import')
#@api.response("201")
class TV_SHOW(Resource):
    @api.response(200, 'OK')
    @api.response(201, 'Created')
    @api.doc(params={'name': '/tv-shows/import?name='})
    def post(self):

        name = parser.parse_args()['name']
        name = name.replace(' ','%20')
        url = 'http://api.tvmaze.com/search/shows?q={}'.format(name)
        json_obj = urlopen(url)
        name = name.lower()
        global idd
        try:
            data = json.load(json_obj)
            length = len(data)
            for items in data:

                item_name = items["show"]["name"].strip()
                item_name =item_name.replace(' ','%20')
                item_name=item_name.lower()
                if item_name == name:
                    sql_id = "select tvmaze_id from COLLECTION"
                    d_id = selectsql1(sql_id)
                    list_id = []
                    for i in d_id:
                        list_id.append(i[0])
                    if items["show"]["id"] in list_id:
                        return {"message": "the content has already existed"}, 400
                    k = datetime.now()
                    k = k.strftime("%Y-%m-%d %H:%M:%S")
                    k = k.replace(' ','-')
                    name2= items["show"]["name"].replace('\'','\'\'')
                    schedule1 = json.dumps(items["show"]["schedule"])
                    rating1 = json.dumps(items["show"]["rating"])
                    network1 = json.dumps(items["show"]["network"])
                    genres1 = json.dumps(items["show"]["genres"])
                    summary1  =  items["show"]["summary"].replace('\'','\'\'')
                    data_1 = (k,items["show"]["id"],name2,items["show"]["type"],items["show"]["language"],str(genres1),items["show"]["status"],items["show"]["runtime"],items["show"]["premiered"],items["show"]["officialSite"],str(schedule1),str(rating1),items["show"]["weight"],str(network1),summary1)

                    sql = "insert into COLLECTION ( last_update, tvmaze_id,name,type, language , genres , status , runtime , premiered , officialSite , schedule , rating , weight ,network ,summary)values('%s',%d,'%s','%s','%s','%s','%s',%d,'%s','%s','%s','%s','%s','%s','%s')"%data_1
                    operationsql(sql)
                    sql_idd = "select id from COLLECTION ORDER BY id asc "
                    d = selectsql1(sql_idd)
                    id_dic = {}
                    for i in range(len(d)):
                        id_dic[i] = d[i][0]
                        if int(d[i][0]) == id:
                            position = i
                        if i == len(d) - 1:
                            max_p = i

                    info ={"id" : id_dic[max_p],
                    "last-update": k,
                    "tvmaze-id" : items["show"]["id"],
                    "_links": {
                        "self": {
                            "herf":"http://127.0.0.1:5000//tv-shows/"+str(id_dic[max_p])
          #"href": "http://[HOST_NAME]:[PORT]/tv-shows/123"
                        }
                    } }

            return info,201
        except:
            return 200#JsonResponse({'flag': False, 'error': '非法访问6'})

@api.route('/tv-shows/<int:id>')
class Question2(Resource):
    @api.response(200, 'OK')
    def get(self,id):
        global idd
        #id = parser.parse_args()['id']
        sql = "select * from COLLECTION where id =" + str(id)
        data_tem =selectsql(sql)
        ret12 =  simplejson.loads(data_tem[12])
        ret14 = simplejson.loads(data_tem[14])
        #data_tem = demjson.encode(data_1)
        info = { "id": data_tem[1],
                 "tvmaze_id": data_tem[0],
                 "last_update": data_tem[2],
                        "name": data_tem[3],
                        "type": data_tem[4],
                        "language": data_tem[5],
                        "genres": eval(data_tem[6]),#re.sub("[^a-zA-Z' ]+", '', data_tem[6]),
                        "status": data_tem[7],
                        "runtime": data_tem[8],
                        "premiered": data_tem[9],
                        "officialSite": data_tem[10],
                        "schedule": eval(data_tem[11]),
                        "rating": ret12,#data_tem[12],eval(data_tem[12]),
                        "weight": data_tem[13],
                        "network": ret14,
                        "summary": data_tem[15],
                        "_link":{
                        "self": {
                            "herf":"http://127.0.0.1:5000/tv-shows/"+str(id)
          #"href": "http://[HOST_NAME]:[PORT]/tv-shows/123"
                        }}
        }
        sql_idd="select id from COLLECTION ORDER BY id asc "
        d = selectsql1(sql_idd)
        id_dic = {}
        for i in range(len(d)):
            id_dic[i] = d[i][0]
            if int(d[i][0]) == id:
                position = i
            if int(i) == len(d)-1:
                max_p = i
        idd = int(id_dic[0])#int(d[0])
        if position>0 :
            info["_link"]["previous"] ={"herf":"http://127.0.0.1:5000/tv-shows/"+str(id_dic[position-1])}
        if position<max_p:
            info["_link"]["next"] ={"herf":"http://127.0.0.1:5000/tv-shows/"+str(id_dic[position+1])}

        return info,200

    @api.response(404, 'Unable to retreive collection.')
    @api.response(400, 'Unable to find collection.')
    @api.response(200, 'OK')
    def delete (self,id):
        sql_idd = "select * from COLLECTION where id = "+str(id)
        d = selectsql(sql_idd)
        if d == None:
            return { 'message': 'Unable to find collection.' }, 404
        info = {
            "message" :"The tv show with id "+str(id)+ " was removed from the database!",
            "id": id
        }
        try:
            sql = "delete from COLLECTION where id ="+ str(id)
            operationsql(sql)
            return info,200
        except:
            info = {
                "message": "Unable to remove collection."
            }
            return info,400

    @api.expect(collection_model)#,validate = True)
    @api.response(200, 'OK')
    @api.doc(description="Update a collection by its ID")
    def patch (self,id):
        sql_idd = "select * from COLLECTION where id = " + str(id)
        d = selectsql(sql_idd)
        if d == None:
            return {'message': 'Unable to find collection.'}, 404
        url1 = "http://127.0.0.1:5000/tv-shows/" + str(id)
        r = request. json
        test= {}
        empty = {'id': 0, 'tvmaze_id': 0, 'last_update': 'string', 'name': 'string', 'type': 'string', 'language': 'string', 'genres': 'string', 'status': 'string', 'runtime': 0, 'premiered': 0, 'officialSite': 'string', 'schedule': 'string', 'rating': 'string', 'weight': 0, 'network': 'string', 'summary': 'string', '_link': 'string'}
        if 'id' in r and id != r["id"]:
            return {"message": "Identifier cannot be changed".format(id)}, 400
        for key in r :
            if key not in collection_model.keys():
                return {"message": "Property {} is invalid".format(key)}, 400

            if r[key] != empty[key]:
                v = r[key]
                if type(r[key])is dict and type(empty[key])is str:
                    #v = ','.join(v)
                    v = json.dumps(v)
                elif type(r[key])is list and type(empty[key])is str:
                    v = json.dumps(v)
                if empty[key] == 'string'and type(r[key])is  str:
                    v = v.replace('\'','\'\'')

                data3 = (key, v, id)

                sql = "Update COLLECTION Set '%s' ='%s' Where Id =%d"%data3
                operationsql(sql)
                test[key] = r[key]
        k = datetime.now()
        k = k.strftime("%Y-%m-%d %H:%M:%S")
        k = k.replace(' ', '-')
        data3 = ('last_update',k,id)
        sql = "Update COLLECTION Set '%s' ='%s' Where Id =%d" % data3
        operationsql(sql)
        info ={
            "id": id,
            "last-update": k,
            "_links": {
                "self": {
                    "href": "http://127.0.0.1:5000/tv-shows/"+str(id)
                }
            }

        }
        return  info,200
parser1 =reqparse.RequestParser()
parser1.add_argument("order_by", type=str)
parser1.add_argument("page", type=str)
parser1.add_argument("page_size", type=str)
parser1.add_argument('filter', type=str)


#@api.route('/tv-shows?order_by=<order_by>&page=<page>&page_size=<page_size>&filter=<filter>')
@api.route('/tv-shows/order_by')
class collectioninterview(Resource):
    #@api.doc(description="'/tv-shows?order_by=<order_by>&page=<page>&page_size=<page_size>&filter=<filter>'")
    @api.response(200,'OK')
    @api.doc(params={'filter': '/tv-shows?/filter='})
    @api.doc(params={'page_size': '/tv-shows?/page_size='})
    @api.doc(params={'page': '/tv-shows?/page='})
    @api.doc(params={'order_by': '/tv-shows?/order_by={id,name,runtime,premiered,rating-average}'})
    def get(self):
        args1 = parser1.parse_args()['order_by']
        args2 = parser1.parse_args()['page']
        args3 = parser1.parse_args()['page_size']
        args4 = parser1.parse_args()['filter']

        if args1 is None:
            args1='+id'
        if args2 is None:
            args2='1'
        if args3 is None:
            args3='100'
        if args4 is None:
            args4='id,name'

        order_list = args1.split(',')
        filter_list = args4.split(',')

        order_string=''
        for k in order_list:
            if "rating-average" in k:
                k=k.replace("rating-average","rating")
            if '+' in k:
                k=k.replace('+','')
                if order_string == '':
                    order_string = order_string + k + " ASC"
                else:
                    order_string = order_string +','+k + " ASC"
            elif '-' in k:
                k = k.replace('-', '')
                if order_string == '':
                    order_string = order_string + k + " DESC"
                else:
                    order_string = order_string + ',' + k + " DESC"
            else:
                return {"message":"please add the special character"},400

        filter_string=''
        for k in filter_list:
            if filter_string == '':
                filter_string =k
            else:
                filter_string = filter_string +','+k

        sql = "select %s from COLLECTION ORDER BY %s"%(args4,order_string)
        data = selectsql1(sql)
        value_list = []
        min_i = (int(args2)-1)*int(args3)
        max_i = int(args2)*int(args3)
        all_page = len(data)/int(args3)+1
        if int(args2)> all_page:

            return {"message":"page is out of range"},400
        for i in range(len(data)):
            if i<min_i or i>=max_i:
                continue
            k = 0
            tem_dic = {}
            for j in filter_list:
                tem_dic[j]=data[i][k]
                k=k+1
            value_list.append(tem_dic)
        info = {"page": args2,
                "page-size": args3,
                "tv-shows": value_list,
                "_link":{
                    "self":{
                        "herf":"http://127.0.0.1:5000/tv-shows?order_by="+args1+"&page="+args2+"&page_size="+args3+"&filter="+args4
                    }
                }
        }
        if int(args2)<all_page:
            info["_link"]["next"]={"herf":"http://127.0.0.1:5000/tv-shows?order_by="+args1+"&page="+str(int(args2)+1)+"&page_size="+str(args3)+"&filter="+args4}

        return info,200

parser2 =reqparse.RequestParser()
parser2.add_argument("format", type=str)#description='which can be either "json" or "image"')
parser2.add_argument("by", type=str)#description='language,genres,status and type')

@api.route('/tv-shows/statistic')
class collectionstatistics(Resource):
    @api.doc(params={'by': '/tv-shows/statistics?by='})
    @api.doc(params={'format': '/tv-shows/statistics?format='})
    @api.response(200, 'OK')
    def get(self):
        #print("000000")
        args1 = parser2.parse_args()['format']
        args2 = parser2.parse_args()['by']
        #print(args2)
        sql = "select %s from COLLECTION"%args2
        #print(sql)
        data = selectsql1(sql)
        content = {}
        type_1 = []
        total_number = len(data)
        newlist = []
        #print("2222222")
        if args2 =="genres":
            for key in data:
                if key[0] != []:
                    newlist = newlist +eval(key[0])
            for item in newlist:
                if item not in type_1:
                    type_1.append(item)
                    content[item] = 1
                else:
                    content[item] = content[item] + 1

        else:
            #print(11111)
            for key in data:
                if key[0] not in type_1:
                    type_1.append(key[0])
                    content[key[0]] = 1
                else:
                    content[key[0]] = content[key[0]]+1
        distribution = {}

        for key in content:
            distribution[key] = round(content[key]/total_number *100,2)
        #print(distribution)
        if args1 == 'json':
            oneday = timedelta(days=1)
            k = datetime.now()-oneday
            k = k.strftime("%Y-%m-%d %H:%M:%S")
            k = k.replace(' ', '-')
            sql = "select count(*) from COLLECTION where last_update > '%s'" %k
            num=selectsql1(sql)

            info={
                "total": total_number,
                "total-updated": num[0][0],
                "values" : distribution }
            return info,200
        else:
            fig = plt.figure()
            plt.bar(range(len(distribution)),list(distribution.values()),align='center')
            plt.xticks(range(len(distribution)),list(distribution.keys()))
            plt.xlabel(args2)
            plt.ylabel('percentage')
            plt.title("the statistics of the existing TV Show")

            img = fig.savefig("img.png")
            #plt.show()
            return send_file("img.png",mimetype = 'image/jpeg')



if __name__ == '__main__':
    cur = con .cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS COLLECTION(
                        tvmaze_id INTEGER unique ,
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        last_update NUMERIC,
                        name text,
                        type text,
                        language text,
                        genres text,
                        status text,
                        runtime INTEGER,
                        premiered NUMERIC,
                        officialSite text,
                        schedule text,
                        rating text,
                        weight INTEGER,
                        network text,
                        summary text,
                        _links text
                        )''')


    con.commit()
    con.close()
    app.run(debug=True)

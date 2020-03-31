import os
import time
import datetime
from app import app
import subprocess
import pymongo
from flask_minify import minify
from htmlmin.minify import html_minify
from forms import CreateEditBeer, SearchBeer, Yeast, Hops, Grains
from flask import Flask, flash, redirect, render_template, request, url_for, Response
import json


class BrewPiLess():
    def __init__(self, beertemp, fridgetemp, beerset, fridgeset, temproom, tempaux, externalvolt, tempmode, modeinint):
        self.beertemp = beertemp
        self.fridgetemp = fridgetemp
        self.beerset = str(beerset)
        self.fridgeset = str(fridgeset)
        self.temproom = str(temproom)
        self.tempaux = str(tempaux)
        self.externalvolt = str(externalvolt)
        self.tempmode = str(tempmode)
        self.modeinint = str(modeinint) 
        #self.path = '/home/hadoop/repo/brewpiless'
        self.path = 'C:/Users/bruno/Desktop/api'
        
    def run_cmd(self, args_list):
        """
        run linux commands
        """
        # import subprocess
        self.args_list = args_list
        print('Running system command: {0}'.format(' '.join(args_list)))
        proc = subprocess.Popen(self.args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        s_output, s_err = proc.communicate()
        s_return =  proc.returncode
        return s_return, s_output, s_err 
        
        
    def GravaArq(self):
        beername = 'beertest' #replace for input
        created = time.strftime("%d/%m/%Y %H:%M:%S")   
        arqformat = time.strftime("%d%m%Y%H%M%S")
        filename = beername+str(arqformat)+'.json'
        content = {'beername':beername, 'created':created, 'beertemp': self.beertemp, 'fridgetemp': self.fridgetemp, 'beerset':self.beerset,'fridgeset':self.fridgeset, 'temproom':self.temproom, 'tempaux':self.tempaux, 'externalvolt': self.externalvolt, 'tempmode':self.tempmode,'modeinint':self.modeinint, 'finished': ''}
        with open(self.path+'/'+filename, 'a+') as arquivo:    
            json.dump(content, arquivo)
            #arquivo.write(str(beername)+';'+str(created)+';'+str(self.beertemp)+';'+str(self.fridgetemp)+';'+str(self.beerset)+';'+str(self.fridgeset)+';'+str(self.temproom)+';'+str(self.tempaux)+';'+str(self.externalvolt)+';'+str(self.tempmode)+';'+str(self.modeinint)+'\n')
        return filename
                
    def ToHDFS(self, arquivo):
        """
        Enviando para HDFS
        """
        #testando se o arquivo existe
        hdfspath = '/datasets/brewpiless/'
        self.arquivo = hdfspath+arquivo
        verarq = ['hdfs', 'dfs', '-test', '-e', self.arquivo]
        ret, out, err = self.run_cmd(verarq)
        
        createarq = ['hdfs', 'dfs', '-put', self.path+'/'+arquivo, hdfspath]
        appendarq = ['hdfs', 'dfs', '-appendToFile', self.path+'/'+arquivo, self.arquivo]
        if ret:
            print('File does not exist')
            #copiando arquivo para HDFS
            self.run_cmd(createarq)
        else:
            print('file exist')           
            #Fazendo Append no HDFS
            self.run_cmd(appendarq)
        return ret, out, err         


@app.route('/')
@app.route('/logs', methods=["GET"])

def index():
    beertemp = request.args.get('TempBeer')
    fridgetemp = request.args.get('TempFridge')
    beerset = request.args.get('BeerSet')
    fridgeset = request.args.get('FridgeSet')
    temproom = request.args.get('TempRoom')
    tempaux = request.args.get('TempAux')
    externalvolt = request.args.get('ExternalVolt')
    tempmode = request.args.get('TempMode')
    modeinint = request.args.get('ModeInInt') 
    print("Temperatura da Breja: {}".format(beertemp))
    print("Temperatura do Fridge: {}".format(fridgetemp))
    print("Config da Breja: {}".format(beerset))
    print("Config do Fridge: {}".format(fridgeset))
    print("Temperatura Ambiente: {}".format(temproom))
    print("Temperatura Auxiliar: {}".format(tempaux))
    print("Voltagem do Spindle: {}".format(externalvolt))
    print("Escala de Temperatura: {}".format(tempmode))
    print("Escala em Inteiro: {}".format(modeinint)) 

    dataobj = BrewPiLess(beertemp, fridgetemp, beerset, fridgeset, temproom, tempaux, externalvolt, tempmode, modeinint)
    arquivo = dataobj.GravaArq()
    #dataobj.ToHDFS(arquivo)
    
    return "collecting from brewpiless"

@app.route('/mainpage') # Main Page
def mainpage():     
    conn = pymongo.MongoClient('mongodb://127.0.0.1', 27017)
    db = conn.brewpiless
    collection = db.beer
    cursor = collection.find_one({"finished": ""}, {'beername': 1, 'beerstyle':1, 'description':1, 'created':1}) 
 
    if cursor:  
        print('iffff') 
        name = cursor['beername']
        style = cursor['beerstyle']
        desc = cursor['description']
        created = cursor['created'] 
        createdformat = created.strftime("%d/%m/%Y %H:%M:%S")
        today = datetime.datetime.now() 
        
        elapsedTime = str(today-created)
        brewing = elapsedTime.replace(':','h')
 
        days = brewing[0:13]+'m'
    return render_template('index.html', name=name, style=style, desc=desc, created=createdformat, days=days) 


@app.route('/beerrecord', methods=["GET","POST"]) # Beer Cadastro 
def beerrecord():
    conn = pymongo.MongoClient('mongodb://127.0.0.1', 27017)
    db = conn.brewpiless
    collection = db.beer    
    
    form = CreateEditBeer()     
    beername = form.beername.data
    beerstyle = form.beerstyle.data
    description =  form.description.data       
    created = datetime.datetime.utcnow()
    finished = form.finished.data            

    beernameid  = request.args.get('beername')    
    print(beernameid)
    if beernameid:
        indb = collection.find_one({"beername": beernameid}, {'_id': 0})
        if indb:
            name = indb['beername']
            style = indb['beerstyle']
            desc = indb['description']
            created = indb['created'] 
            finished = indb['finished'] 
            
            print("achou no db")
            print(indb)
            print(name)
    else:
        print("nao achou")
    
    values = {"beername": beername, "beerstyle":beerstyle, "description":description, "created": created, "finished":''}
 
#    if form.validate():
#        verbeer = collection.find_one({"beername": beername})
#        if verbeer:
#            flash("Ja exist")
#            collection.update_one({"beername": beername}, {"beerstyle":beerstyle}, {"finished":''}, upsert=False)
#            flash("updated ?")
#        else:
#            beerinserted = collection.insert_one(values)            
#            flash("New beer included!")
    conn.close()  
    return render_template('CadastroBreja.html', form=form, name=name, style=style, desc=desc, created=created, finished=finished)
   
  

@app.route('/beersearch', methods=["GET", "POST"]) # Beer Search
def beersearch():
    conn = pymongo.MongoClient('mongodb://127.0.0.1', 27017)
    db = conn.brewpiless
    collection = db.beer    
    
    form = SearchBeer()     
    beername = form.beername.data
    beerstyle = form.beerstyle.data
    #urlid  = request.args.get('id')
    ret = ''  
    if form.validate_on_submit():     
        if beername == '' and beerstyle == '':
           #busca tudo  
           ret = list(collection.find({}, {'_id': 0})) 
 
        elif beername != '':
           #busca NAME           
           ret2 = collection.find({"beername": beername})
           if ret2:
               ret = list(ret2)
 
        else:
        #busca Style
           ret = list(collection.find({"beerstyle": beerstyle}))
                   
    conn.close()  
    return render_template('SearchResult.html', form=form, ret=ret) 
                                
                    

#def getdata():
#    conn = pymongo.MongoClient('mongodb://127.0.0.1', 27017)
#    db = conn.brewpiless
#    collection = db.brewpiless
#
#    rdata = list(collection.find() )
#    print(rdata)
#    if rdata: 
#        # create an empty results object
#        value_list = []
#        data_list = []
#        # now loop through all of the documents in the cursor
#        ponto = []
#        for doc in rdata:
#            ponto.append([doc.get('created'), float(doc.get('beertemp'))])
#            for keys in doc.keys():
#                if keys != '_id':
#                    value_list = [keys]
#                    #print(value_list)
#                   data_list.append(value_list)           
#        print(ponto)
#        return ponto
#    else:
#        print("Cursor is empty")
#        # return an empty result
#        return "[]"



@app.route('/analytics', methods=["GET", 'POST']) # Analytics
def analytics():     
    return render_template('Analytics.html') 
 
 

@app.route('/chart-live-data')
def chart_live_data():
    def getlivedata():
        while True:
            conn = pymongo.MongoClient('mongodb://127.0.0.1', 27017)
            
            with conn:
                db = conn.brewpiless
                collection = db.brewpiless
                cursor = collection.find({}, {'created': 1, 'beertemp':1, 'fridgetemp':1}) 
                 
                if cursor:   
                    for row in cursor:  
                            json_data = json.dumps({'time':row['created'], 'value':row['beertemp'], 'value2':row['fridgetemp']})
                            print(json_data)
                            #print('{0} {1}'.format(row['created'], row['beertemp']))
                           # json_data = json.dumps(
                           #     {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': random.random() * 100})
                            yield f"data:{json_data}\n\n"
                            time.sleep(5)
                else:
                    print("Cursor is empty")  
                conn.close()  
    return Response(getlivedata(), mimetype='text/event-stream')
#adding new axe



@app.route('/chart-data')
def chart_data():
    def getdata():
        while True:
            conn = pymongo.MongoClient('mongodb://127.0.0.1', 27017)
            
            with conn:
                db = conn.brewpiless
                collection = db.brewpiless
                cursor = collection.find({}, {'created': 1, 'beertemp':1, 'fridgetemp':1}) 
                print(cursor)  
                if cursor:   
                    for row in cursor:  
                        json_data = json.dumps({'time':row['created'], 'value':row['beertemp']})
                        print(json_data)
                        #print('{0} {1}'.format(row['created'], row['beertemp']))
                       # json_data = json.dumps(
                       #     {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': random.random() * 100})
                        yield f"data:{json_data}\n\n"
                        time.sleep(1)
                else:
                    print("Cursor is empty")  
                conn.close()  
    return Response(getdata(), mimetype='text/event-stream') 
    
    
  
@app.route('/hops', methods=["GET", 'POST']) # HOPS
def hops():     
    conn = pymongo.MongoClient('mongodb://127.0.0.1', 27017)
    db = conn.brewpiless
    collection = db.hops    
    
    form = Hops()      
    
    Hop = form.Hop.data 
    Type = form.Type.data 
    Origin = form.Origin.data     
    ret = ''  
    if form.validate_on_submit():    
        if Hop == '' and Type == '' and Origin == '' :
           #busca tudo  
           ret = list(collection.find({}, {'_id': 0, 'Hop': 1, 'Origin':1, 'Type':1, 'Alpha':1, 'Beta':1, 'Notes':1}))                     
           print(ret)           
           print('if')
        elif Hop != '':
           #busca NAME        
           print('elif')           
           ret = collection.find({"Hop": Hop},  {'_id': 0, 'Hop': 1, 'Origin':1, 'Type':1, 'Alpha':1, 'Beta':1, 'Notes':1})                    
           print(type(ret))
           
           print(ret)
        elif Type != '':
           #busca NAME        
           print('elif')           
           ret = list(collection.find({"Type": Type},  {'_id': 0, 'Hop': 1, 'Origin':1, 'Type':1, 'Alpha':1, 'Beta':1, 'Notes':1}))                     
           print(type(ret))
           print(ret)           
        else:
        #busca Style
           print('else')        
           ret = list(collection.find({"Origin": Origin},  {'_id': 0, 'Hop': 1, 'Origin':1, 'Type':1, 'Alpha':1, 'Beta':1, 'Notes':1}))                     
           print(ret)                       
    conn.close() 
    return render_template('hops.html', form=form, ret=ret)      
    

@app.route('/grains', methods=["GET", 'POST']) # GRAINS
def grains():     
    conn = pymongo.MongoClient('mongodb://127.0.0.1', 27017)
    db = conn.brewpiless
    collection = db.grains    
    
    form = Grains()      
    
    Hop = form.Hop.data 
    Type = form.Type.data 
    Origin = form.Origin.data     
    ret = ''  
    if form.validate_on_submit():    
        if Hop == '' and Type == '' and Origin == '' :
           #busca tudo  
           ret = list(collection.find({}, {'_id': 0, 'Hop': 1, 'Origin':1, 'Type':1, 'Alpha':1, 'Beta':1, 'Notes':1}))                     
           print(ret)           
           print('if')
        elif Hop != '':
           #busca NAME        
           print('elif')           
           ret = collection.find({"Hop": Hop},  {'_id': 0, 'Hop': 1, 'Origin':1, 'Type':1, 'Alpha':1, 'Beta':1, 'Notes':1})                    
           print(type(ret))
           
           print(ret)
        elif Type != '':
           #busca NAME        
           print('elif')           
           ret = list(collection.find({"Type": Type},  {'_id': 0, 'Hop': 1, 'Origin':1, 'Type':1, 'Alpha':1, 'Beta':1, 'Notes':1}))                     
           print(type(ret))
           print(ret)           
        else:
        #busca Style
           print('else')        
           ret = list(collection.find({"Origin": Origin},  {'_id': 0, 'Hop': 1, 'Origin':1, 'Type':1, 'Alpha':1, 'Beta':1, 'Notes':1}))                     
           print(ret)                       
    conn.close() 
    return render_template('grains.html', form=form, ret=ret)      


    
@app.route('/recipes', methods=["GET", 'POST']) # recipes
def recipes():   
    conn = pymongo.MongoClient('mongodb://127.0.0.1', 27017)
    db = conn.brewpiless
    collection = db.beer    
    
    form = SearchBeer()     
    beername = form.beername.data
    beerstyle = form.beerstyle.data
    ret = ''  
    if form.validate_on_submit():     
        print('if')
    else:
        print('else')
    conn.close()  
    return render_template('recipes.html', form=form) 
 
 
 
  
@app.route('/yeasts', methods=["GET", 'POST']) # YEAST
def yeasts():     
    conn = pymongo.MongoClient('mongodb://127.0.0.1', 27017)
    db = conn.brewpiless
    collection = db.yeast    
    
    form = Yeast()     
    
    yeastname = form.yeastname.data
    description = form.description.data
    yeasttype = form.yeasttype.data   
    ret = ''  
    if form.validate_on_submit():     
        print(form)
        if yeastname == '' and yeasttype == '':
           #busca tudo  
           ret = list(collection.find({}, {'_id': 0, 'name': 1, 'description':1, 'yeastType':1, 'attenuationMin':1, 'attenuationMax':1, 'fermentTempMin':1, 'fermentTempMax':1, 'alcoholToleranceMin':1, 'alcoholToleranceMax':1, 'supplier':1, 'yeastFormat':1}))                     
           print(ret)           
           print('if')
        elif yeastname != '':
           #busca NAME        
           print('elif')           
           ret = list(collection.find_one({"name": yeastname}, {'_id': 0, 'name': 1, 'description':1, 'yeastType':1, 'attenuationMin':1, 'attenuationMax':1, 'fermentTempMin':1, 'fermentTempMax':1, 'alcoholToleranceMin':1, 'alcoholToleranceMax':1, 'supplier':1, 'yeastFormat':1})) 
           print(type(ret))
           print(ret)
        else:
        #busca Style
           print('else')        
           ret = list(collection.find({"yeastType": yeasttype}, {'_id': 0, 'name': 1, 'description':1, 'yeastType':1, 'attenuationMin':1, 'attenuationMax':1, 'fermentTempMin':1, 'fermentTempMax':1, 'alcoholToleranceMin':1, 'alcoholToleranceMax':1, 'supplier':1, 'yeastFormat':1}))
           print(ret)                       
    conn.close() 
    return render_template('yeast.html', form=form, ret=ret)  


@app.route('/yeastrecord', methods=["GET", 'POST']) # YEAST
def yeastrecord():     
    conn = pymongo.MongoClient('mongodb://127.0.0.1', 27017)
    db = conn.brewpiless
    collection = db.yeast    
         
 
    yeastnameid  = request.args.get('yeastname')    
    print(yeastnameid)
    if yeastnameid:
        indb = collection.find_one({"name": yeastnameid}, {'_id': 0, 'name': 1, 'description':1, 'yeastType':1, 'attenuationMin':1, 'attenuationMax':1, 'fermentTempMin':1, 'fermentTempMax':1, 'alcoholToleranceMin':1, 'alcoholToleranceMax':1, 'supplier':1, 'yeastFormat':1})
        if indb:
            name = indb['name']
            description = indb['description']            
            yeastType = indb['yeastType']
            attMin = indb['attenuationMin']
            attMax = indb['attenuationMax'] 
            ferTempMin = indb['fermentTempMin'] 
            ferTempMax = indb['fermentTempMax'] 
            alcoholTolMin = indb['alcoholToleranceMin'] 
            alcoholTolMax = indb['alcoholToleranceMax'] 
            supplier = indb['supplier'] 
            yeastFormat = indb['yeastFormat'] 

            
            print("achou no db")
            print(indb)
            print(name)
    else:
        print("nao achou")
    
    conn.close() 
    return render_template('yeast.html', name=name, description=description, yeastType=yeastType, attMin=attMin, attMax=attMax, ferTempMin=ferTempMin, ferTempMax=ferTempMax, alcoholTolMin=alcoholTolMin, supplier=supplier, yeastFormat=yeastFormat)        
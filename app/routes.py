import os
import time
import datetime
from app import app
import subprocess
import pymongo
from flask_minify import minify
from htmlmin.minify import html_minify
from forms import CreateEditBeer, CreateEditHop, CreateEditGrain, CreateEditYeast,CreateRecipe, SearchBeer, Yeasts, Hops, Grains
from flask import Flask, flash, redirect, render_template, request, url_for, Response, jsonify
import json
import pandas as pd
import matplotlib.pyplot as plt 

conn = pymongo.MongoClient('mongodb://127.0.0.1', 27017)
db = conn.brewpiless
    
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


@app.route('/')
@app.route('/mainpage') # Main Page
def mainpage():       
    collection = db.beer
    cursor = collection.find_one({"finished": ""}, {'beername': 1, 'beerstyle':1, 'description':1, 'created':1}) 
 
    if cursor:   
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
    collection = db.beer    
    
    form = CreateEditBeer()     
    beername = form.beername.data
    beerstyle = form.beerstyle.data
    description =  form.description.data       
    created = datetime.datetime.utcnow()
    finished = form.finished.data            
       
    values = {"beername": beername, "beerstyle":beerstyle, "description":description, "created": created, "finished":''}
    
    beernameid  = request.args.get('beername')    
    #variables for return
    name = ''
    style = ''
    desc = ''
    created = ''
    finished = ''

    if form.validate():
        verbeer = collection.find_one({"beername": beername})
        
        if verbeer:
            flash("Beer already exists")
            collection.update_one({"beername": beername}, {"beerstyle":beerstyle}, {"finished":'finished'}, upsert=False)

        else:
            beerinserted = collection.insert_one(values)            
            flash("New beer included!")

    
    elif beernameid:
        indb = collection.find_one({"beername": beernameid}, {'_id': 0})
        if indb:
            name = indb['beername']
            style = indb['beerstyle']
            desc = indb['description']
            created = indb['created'] 
            finished = indb['finished'] 
    
    conn.close()  
    return render_template('CadastroBreja.html', form=form, name=name, style=style, desc=desc, created=created, finished=finished)
   
  

@app.route('/beersearch', methods=["GET", "POST"]) # Beer Search
def beersearch():  
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



@app.route('/analyticsOLD', methods=["GET", 'POST']) # Analytics
def analyticsOLD():             

    beer = 'beertest'  
    collection = db.brewpiless    
    
    df = pd.DataFrame(list(collection.find({'beername':beer}, {'_id':0,'beername': 1, 'created':1, 'beertemp':1, 'fridgetemp':1, 'beerset':1, 'fridgeset':1})))

    df['created'] = pd.to_datetime(df['created'])
    df['beertemp'] = df['beertemp'].astype('float') 
    df['fridgetemp'] = df['fridgetemp'].astype('float') 
    df['beerset'] = df['beerset'].astype('float') 
    df['fridgeset'] = df['fridgeset'].astype('float') 
    df = df.sort_values('created', ascending=True) 
    tam = df.count()
 
    label = df['created']
    y1 =  df['beertemp']
    y2 = df['fridgetemp']
    y3 = df['beerset']
    y4 = df['fridgeset']   
    
    plt.style.use('seaborn-whitegrid')    
    fig, ax = plt.subplots()
    plt.rcParams["figure.figsize"] = [16,9]
    plt.plot(label,y1, label='Beer Temp', linewidth=2)
    plt.plot(label,y2, label='Fridge Temp', linewidth=2)
    plt.plot(label,y3, label='Beer Set', linewidth=2)
    plt.plot(label,y4, label='Fridge Set', linewidth=2)
    
    plt.title(beer, fontsize=14, fontweight=0, color='blue')
    # Add legend
    plt.legend(loc=4, ncol=1,fontsize='small')


    # set custom tick labels
    ax.set_xticklabels(label, rotation=45, horizontalalignment='right')
    
    path = '/css/images/icons/'+beer+'.png'
    print(path)
    plt.savefig('C:/Users/bceolincamar/Documents/GitHub/homebrew/static/css/images/icons/'+beer+'.png')
    
    return render_template('Analytics.html', path = path) 

 
@app.route('/analytics', methods=["GET"]) # Analytics
def data():             
    
    beer = 'beertest'  
    collection = db.brewpiless     
    result = list(collection.find({'beername':beer}, {'_id':0,'beername': 1, 'created':1, 'beertemp':1, 'fridgetemp':1, 'beerset':1, 'fridgeset':1}))
    
#    df = pd.DataFrame(list(collection.find({'beername':beer}, {'_id':0,'beername': 1, 'created':1, 'beertemp':1, 'fridgetemp':1, 'beerset':1, 'fridgeset':1})))

  
    
    return jsonify({'results': result['created','beertemp', 'fridgetemp', 'beerset', 'fridgeset':]})  
 

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
    
    
  
@app.route('/hopssearch', methods=["GET", 'POST']) # HOPS
def hops():      
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
           print('if')
        elif Hop != '':
           #busca NAME        
           print('elif')           
           ret = collection.find({"Hop": Hop},  {'_id': 0, 'Hop': 1, 'Origin':1, 'Type':1, 'Alpha':1, 'Beta':1, 'Notes':1})                    
           print(type(ret)) 
        elif Type != '':
           #busca NAME        
           print('elif')           
           ret = list(collection.find({"Type": Type},  {'_id': 0, 'Hop': 1, 'Origin':1, 'Type':1, 'Alpha':1, 'Beta':1, 'Notes':1}))                     
           print(type(ret)) 
        else:
        #busca Style
           print('else')        
           ret = list(collection.find({"Origin": Origin},  {'_id': 0, 'Hop': 1, 'Origin':1, 'Type':1, 'Alpha':1, 'Beta':1, 'Notes':1}))                     
                 
    conn.close() 
    return render_template('hops.html', form=form, ret=ret)      
    
@app.route('/hopsrecord', methods=["GET","POST"]) # Beer Cadastro 
def hopsrecord():
 
    collection = db.hops    
    
    form = CreateEditHop()     
    hop = form.hop.data
    origin = form.origin.data
    hoptype =  form.hoptype.data       
    alpha = form.alpha.data       
    beta = form.beta.data            
    notes = form.notes.data 
        
    values = {"Hop": hop, "Origin":origin, "Type":hoptype, "Alpha":alpha, "Beta":beta, "Notes":notes}
    
    hopnameid  = request.args.get('Hop')    
    #variables for return
    Hop = ''
    Origin = ''
    Type = ''
    Alpha = ''
    Beta = ''
    Notes = ''
    
    if form.validate():
        verhop = collection.find_one({"Hop": hop})
        
        if verhop:
            flash("Hop details updated !")
            collection.update_one({"Hop": hop}, {'$set':{"Origin":origin, "Type":hoptype, "Alpha":alpha, "Beta":beta, "Notes":notes}}, upsert=False)

        else:
            beerinserted = collection.insert_one(values)            
            flash("New Hop included!")
    
    elif hopnameid:
        indb = collection.find_one({"Hop": hopnameid}, {'_id': 0})
        if indb:
            Hop = indb['Hop']
            Origin = indb['Origin']
            Type = indb['Type']
            Alpha = indb['Alpha'] 
            Beta = indb['Beta'] 
            Notes = indb['Notes']            
    
    conn.close()  
    return render_template('hopsrecord.html', form=form, Hop=Hop, Origin=Origin, Type=Type, Alpha=Alpha, Beta=Beta, Notes=Notes)
   
@app.route('/grainssearch', methods=["GET", 'POST']) # GRAINS
def grains():       
    collection = db.grains    
    
    form = Grains()      
    
    Grain = form.Grain.data 
    Origin = form.Origin.data        
    ret = ''  
    if form.validate_on_submit():    
        if Grain == '' and Origin == '' :
           #busca tudo  
           ret = list(collection.find({}, {'_id': 0, 'Grain': 1, 'Origin':1, 'Mash':1, 'Color':1, 'Power':1, 'Potential':1, 'MaxPercent':1, 'Notes':1}))                     
 
        elif Grain != '':
           #busca NAME            
           ret = collection.find({"Grain": Grain}, {'_id': 0, 'Grain': 1, 'Origin':1, 'Mash':1, 'Color':1, 'Power':1, 'Potential':1, 'MaxPercent':1, 'Notes':1})                    
    
        else:
        #busca Style 
           ret = list(collection.find({"Origin": Origin},  {'_id': 0,  'Grain': 1, 'Origin':1, 'Mash':1, 'Color':1, 'Power':1, 'Potential':1, 'MaxPercent':1, 'Notes':1}))                     
                       
    conn.close() 
    return render_template('grains.html', form=form, ret=ret)      

@app.route('/grainsrecord', methods=["GET","POST"]) # Beer Cadastro 
def grainsrecord():  
    collection = db.grains    
    
    form = CreateEditGrain()     
    grain = form.grain.data
    origin = form.origin.data
    mash =  form.mash.data       
    color = form.color.data       
    power = form.power.data            
    potential = form.potential.data 
    maxp = form.maxp.data 
    notes = form.notes.data 
    
    values = {"Grain": grain, "Origin":origin, "Mash":mash, "Color":color, "Power":power, "Potential":potential, "MaxPercent":maxp, "Notes":notes}
    
    grainnameid  = request.args.get('Grain')    
    #variables for return
    Grain = ''
    Origin = ''
    Mash = ''
    Color = ''
    Power = ''
    Potential = ''
    MaxPercent = ''    
    Notes = ''
    
    if form.validate():
        verhop = collection.find_one({"Grain": grain})
        
        if verhop:
            flash("Grain details updated !")
            collection.update_one({"Grain": grain}, {'$set':{"Origin":origin, "Mash":mash, "Color":color, "Power":power, "Potential":potential, "MaxPercent":maxp, "Notes":notes}}, upsert=False)

        else:
            graininserted = collection.insert_one(values)            
            flash("New Grain included!")
    
    elif grainnameid:
        indb = collection.find_one({"Grain": grainnameid}, {'_id': 0})
        if indb:
            Grain = indb['Grain']
            Origin = indb['Origin']
            Mash = indb['Mash']
            Color = indb['Color'] 
            Power = indb['Power'] 
            Potential = indb['Potential'] 
            MaxPercent = indb['MaxPercent'] 
            Notes = indb['Notes']            
    
    conn.close()  
    return render_template('grainsrecord.html', form=form, Grain=Grain, Origin=Origin, Mash=Mash, Color=Color, Power=Power, Potential=Potential, MaxPercent=MaxPercent, Notes=Notes)



@app.route('/yeastssearch', methods=["GET", 'POST']) # YEAST
def yeastssearch():       
    collection = db.yeast    
    
    form = Yeasts()     
    
    Yeast = form.Yeast.data
    Yeastlab = form.Yeastlab.data
    Yeasttype = form.Yeasttype.data   
    
    ret = ''  
    if form.validate_on_submit():     
        print(form)
        if Yeast == '' and Yeasttype == '':
           #busca tudo  
           ret = list(collection.find({}, {'_id': 0, 'Name': 1, 'Lab':1, 'Type':1, 'Form':1, 'Temp':1, 'Attenuation':1, 'Flocculation':1, 'Notes':1}))                     
           print(ret)           
           print('if')
        elif Yeast != '':
           #busca NAME        
           print('elif')           
           ret =  collection.find({"Name": Yeast}, {'_id': 0, 'Name': 1, 'Lab':1, 'Type':1, 'Form':1, 'Temp':1, 'Attenuation':1, 'Flocculation':1, 'Notes':1})               
               
           print(type(ret))
           print(ret)
        else:
        #busca Style
           print('else')        
           ret = list(collection.find({"Type": Yeasttype}, {'_id': 0, 'Name': 1, 'Lab':1, 'Type':1, 'Form':1, 'Temp':1, 'Attenuation':1, 'Flocculation':1, 'Notes':1}))
           print(ret)                       
    conn.close() 
         
    return render_template('yeast.html', form=form, ret=ret)  

@app.route('/yeastsrecord', methods=["GET","POST"]) # Beer Cadastro 
def yeastsrecord():  
    collection = db.yeast   
    
    form = CreateEditYeast()    
    name = form.yeast.data
    lab = form.lab.data
    typey =  form.typey.data       
    formato =  form.formato.data       
    temp = form.temp.data       
    attenuation = form.att.data            
    flocculation = form.flo.data 
    notes = form.notes.data  
    values = {"Name": name, "Lab":lab, "Type":typey, "Temp":temp, "Attenuation":attenuation, "Flocculation":flocculation, "Notes":notes}
 
    yeastnameid  = request.args.get('Name')    
    #variables for return
    Name = ''
    Lab = ''
    Typey = ''
    Formato = ''
    Temp = ''
    Attenuation = ''
    Flocculation = ''    
    Notes = ''
    
    if form.validate():
        veryeast = collection.find_one({"Name": name})
        
        if veryeast:
            flash("Yeast details updated !")
            collection.update_one({"Name": name}, {'$set':{"Lab":lab, "Type":typey, "Temp":temp, "Attenuation":attenuation, "Flocculation":flocculation, "Notes":notes}}, upsert=False)

        else:
            yeastinserted = collection.insert_one(values)            
            flash("New Yeast included!")
    
    elif yeastnameid:
        indb = collection.find_one({"Name": yeastnameid}, {'_id': 0})
        if indb:
            Name = indb['Name']
            Lab = indb['Lab']
            Typey = indb['Type']
            Formato = indb['Form'] 
            Temp = indb['Temp'] 
            Attenuation = indb['Attenuation'] 
            Flocculation = indb['Flocculation'] 
            Notes = indb['Notes']            
    
    conn.close()  
    return render_template('yeastrecord.html', form=form, Name=Name, Lab=Lab, Typey=Typey, Formato=Formato, Temp=Temp, Attenuation=Attenuation, Flocculation=Flocculation, Notes=Notes)


    
@app.route('/recipes', methods=["GET", 'POST']) # recipes 
def recipes():     
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
 
 
 
@app.route('/recipesrecord', methods=["GET", 'POST']) # recipes
def dropdown():     


    form = CreateRecipe()     
    crecipe = db.recipes
    cgrains = db.grains
    chops = db.hops
    cyeasts = db.yeast
    Glist = []
    Hlist = []
    Ylist = []
    
    Grains = list(cgrains.find({}, {'_id': 0, 'Grain': 1}))
    
    for doc in Grains:
        for v in doc.values():
            Glist.append(v) 
     
    Hops = list(chops.find({}, {'_id': 0, 'Hop': 1}))
    for doc in Hops:
        for v in doc.values():
            Hlist.append(v) 
     
 
    Yeasts = list(cyeasts.find({}, {'_id': 0, 'Name': 1}))
    for doc in Yeasts:
        for v in doc.values():
            Ylist.append(v) 
     
    if request.method == 'POST':
        name = form.name.data
        selgrains = request.form.getlist('grains')
        selhops = request.form.getlist('hop')
        selyeast = request.form.getlist('yeast')
        fermentables = form.fermentable.data
                        
        print(selgrains)
        print(selhops)        
        print(selyeast) 
        print(name)        
        print(fermentables) 
        listgrain = []
        for grain in selgrains:
            print("aqui "+grain)
            r = list(cgrains.find({"Grain": grain}, {'_id':1}))
            listgrain.append(r)
            
            
        values = {"Name":name, "Grains": listgrain, "Hops": selyeast, "Yeasts": selyeast, "Fermentables": fermentables }
        print(values)
#       checkrecipe = crecipe.find_one({"Name": name})
        
#        if checkrecipe:
#           flash("Recipe updated !")
#           collection.update_one({"Name": name}, {'$set':{"Lab":lab, "Type":typey, "Temp":temp, "Attenuation":attenuation, "Flocculation":flocculation, "Notes":notes}}, upsert=False)
#
#       else:
#           recipeinserted = collection.insert_one(values)            
#            flash("Recipe included!")
#   
# 
    return render_template('recipesrecord.html',Glist=Glist, Hlist=Hlist, Ylist=Ylist, form=form)
    
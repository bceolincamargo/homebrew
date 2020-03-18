import os
import flask as fl
import time
import datetime
from app import app
import subprocess
import pymongo
from flask_minify import minify
from htmlmin.minify import html_minify
from forms import CreateEditBeer
 



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
        self.path = '/home/hadoop/coletor/app/output'
        
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
        created = time.strftime("%d/%m/%Y, %H:%M:%S")       
        filename = beername+'.csv'
        with open(self.path+'/'+filename, 'a+') as arquivo:
            arquivo.write(beername+';'+created+';'+self.beertemp+';'+self.fridgetemp+';'+self.beerset+';'+self.fridgeset+';'+self.temproom+';'+self.tempaux+';'+self.externalvolt+';'+self.tempmode+';'+self.modeinint+'\n')
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
    beertemp = fl.request.args.get('TempBeer')
    fridgetemp = fl.request.args.get('TempFridge')
    beerset = fl.request.args.get('BeerSet')
    fridgeset = fl.request.args.get('FridgeSet')
    temproom = fl.request.args.get('TempRoom')
    tempaux = fl.request.args.get('TempAux')
    externalvolt = fl.request.args.get('ExternalVolt')
    tempmode = fl.request.args.get('TempMode')
    modeinint = fl.request.args.get('ModeInInt') 
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
    #arquivo = dataobj.GravaArq()
    #dataobj.ToHDFS(arquivo)
    
    return "collecting from brewpiless"

@app.route('/mainpage') # Main Page
def mainpage():     
    return fl.render_template('index.html') 

#@app.route('/beerrecord', methods=["GET"]) # Cadastro
   
#def cadastro():
#    beername = None
#    beername = None   
#
#   beername = fl.request.args.get('beername')
#    beerstyle = fl.request.args.get('beerstyle')
#
#    if beerstyle and brejastyle:  
#        beername = str(beername)
#        beerstyle = str(beerstyle)
#
#    return fl.render_template('CadastroBreja.html', beername=beername,    
#                                         beerstyle=beerstyle)


@app.route('/beerrecord', methods=["GET","POST"]) # Beer Cadastro 
def beerrecord():
    conn = pymongo.MongoClient('mongodb://192.168.20.15', 27017)
    db = conn.brewpiless
    collection = db.beer      
    print("oiiii")
    form = CreateEditBeer()    
    print(form.errors)
    beername = form.beername.data
    beerstyle = form.beerstyle.data
    description =  form.description.data       
    created = datetime.datetime.utcnow()
    print("tchau")
    print(form)
    print(form.errors)    
    print(description)
    if form.validate_on_submit():      
        flash("Successfully created a new book")         
        print(form.errors)
    if form.is_submitted():
        print(form.errors)
        print "submitted"
    if form.validate():
        print "valid"
    if form.validate_on_submit():
        flash("Successfully created a new book")     
        print(description)
        #verbeer = collection.find_one({"beername": beername})
        #values = {"beername": beername, "beerstyle":beerstyle, "description":description, "created": created}
        #beerinserted = collection.insert_one(values)            
        conn.close()  
    return fl.render_template('CadastroBreja.html, form=form') 
   
  

@app.route('/beersearch', methods=["GET"]) # Beer Search
def beersearch():
    beername = fl.request.form.get('brejaname') 
    beerstyle = fl.request.form.get('brejastyle')     
    return fl.render_template('BrejaSearch.html', beername=beername, beerstyle=beerstyle) 
                
@app.route('/beerfind', methods=["GET","POST"]) # Beer Search
def beerfind():
    conn = pymongo.MongoClient('mongodb://192.168.20.15', 27017)
    db = conn.brewpiless
    collection = db.beer    
    beername = fl.request.form.get('brejaname') 
    beerstyle = fl.request.form.get('brejastyle')   
    if beername == '' and beerstyle == '':
        ret = 'Please, type at least one field'
    elif beername != '':
        found = collection.find_one({"brejaname": beername}) 
    elif beerstyle != '':
        found = collection.find_one({"type": beerstyle})         
    else:
        msg = 'Beer not found'
    conn.close()
    return fl.render_template('BrejaSearch.html', found=found) 
                                
                
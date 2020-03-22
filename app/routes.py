import os
import time
import datetime
from app import app
import subprocess
import pymongo
from flask_minify import minify
from htmlmin.minify import html_minify
from forms import CreateEditBeer, SearchBeer
from flask import Flask, flash, redirect, render_template, request, url_for



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
        self.path = '/home/hadoop/repo/brewpiless'
        
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
    #arquivo = dataobj.GravaArq()
    #dataobj.ToHDFS(arquivo)
    
    return "collecting from brewpiless"

@app.route('/mainpage') # Main Page
def mainpage():     
    return render_template('index.html') 


@app.route('/beerrecord', methods=["GET","POST"]) # Beer Cadastro 
def beerrecord():
    conn = pymongo.MongoClient('mongodb://192.168.20.15', 27017)
    db = conn.brewpiless
    collection = db.beer    
    
    form = CreateEditBeer()     
    beername = form.beername.data
    beerstyle = form.beerstyle.data
    description =  form.description.data       
    created = datetime.datetime.utcnow()
    finished = form.finished.data       
    values = {"beername": beername, "beerstyle":beerstyle, "description":description, "created": created, "finished":''}
    if form.validate():
        verbeer = collection.find_one({"beername": beername})
        if verbeer:
            flash("Ja exist")
            collection.update_one({"beername": beername}, {"beerstyle":beerstyle}, {"finished":''}, upsert=False)
            flash("updated ?")
        else:
            beerinserted = collection.insert_one(values)            
            flash("New beer included!")
        conn.close()  
    return render_template('CadastroBreja.html', form=form)
   
  

@app.route('/beersearch', methods=["GET", "POST"]) # Beer Search
def beersearch():
    conn = pymongo.MongoClient('mongodb://192.168.20.15', 27017)
    db = conn.brewpiless
    collection = db.beer    
    
    form = SearchBeer()     
    beername = form.beername.data
    beerstyle = form.beerstyle.data
    ret = ''
    print(form)
    print(str(beername)+" beername")
    print(str(beerstyle)+" beerstyle")
    print(form.validate_on_submit())
    flash(form.errors)
    if form.validate_on_submit():     
        if beername == '' and beerstyle == '':
           #busca tudo  
           ret = db.collection.find()
           flash("anything")
           print(beerstyle+" style IF")           
        elif beername != '':
           #busca NAME
           ret = db.collection.find_one(beername)
           print(ret)
           print(beerstyle+" style ELSEIF")           
           flash("elseIF")           
        else:
        #busca Style
           ret = db.collection.find_one(beerstyle)     
           print(ret)
           print(beerstyle+" style else")
           flash("ELSE")
    conn.close()
    return render_template('BrejaSearch.html', form=form, ret=ret) 
                                
                
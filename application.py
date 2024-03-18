from flask import *
from datetime import datetime, timedelta
import os
import csv
import json
import requests

app = Flask(__name__)

open_time = 0 #voting open time (seconds since epoch)
close_time = 0 #voting close time (seconds since epoch)

finns = [] #members in the nation of Finland, when the application is started
candidates = [] #candidates in the election
voted_ips = [] #IPs of people who already voted
voted_names = [] #usernames of people who already voted
logfile = "" #logfile location


#utility thingies

#ordinal conversion oneliner, stolen from https://codegolf.stackexchange.com/questions/4707/outputting-ordinal-numbers-1st-2nd-3rd#answer-4712
ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4]) 




#logging logic

def start_logger():
    global logfile
    
    print("Initiating logger...")
    if not os.path.exists("log"):
        print("Log directory not found, creating...")
        os.makedirs("log")
    logfile = "log/"+datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3]+".txt" #log file name is timestamped
    with open(logfile, "x") as file:
        file.write("-----------------------Log start-------------------------------\n")
    print("Logger initialized successfully");


def log(input): #we want to only log outputs from the actual voting site flask output, so I'm doing this'
    global logfile

    print(input)
    with open(logfile, "a") as file:
        file.write(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S ")+input+"\n")




#csv reading/writing logic

def file_setup():
    if not os.path.exists("results.csv"):
       log("Results file doesn't exist, creating...")
       with open("results.csv","x") as file:
           f_line="Timestamp,IP,voter name,"
           for i in range(len(candidates)):
               f_line+=ordinal(i+1)+" choice,"
           file.write(f_line+"\n")
       log("Results file creation successful")

unwritten = [] #cannot write into csv file if it is open in excel, postpone for writing later
def write_results(ip,username,results):
    file_setup()
    data_to_write = [datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),ip,username]
    for i in results.values():
        data_to_write.append(i)
        
    removequeue = []
    try:
        log("Attempting to write current log data into file...")
        with open("results.csv","a") as file:    
            for i in unwritten: #postponed data
                log("Writing postponed vote: "+str(i)+" into file...")
                file.write(",".join(i)+"\n")    
                log("Success")
                removequeue.append(i)    
            log("Writing current vote into file...")
            file.write(",".join(data_to_write)+"\n")
        log("All votes written into file succesfully")
        
    except:
        unwritten.append(data_to_write)
        log("Writing vote into file failed, postponing write...")
        log("Raw data: "+str(data_to_write))
        
    #remove postponed data from postponed data queue (I can't just clear unwritten, because it might fail mid-write and then some votes would get lost)
    for i in removequeue: 
        unwritten.remove(i)
    removequeue.clear()
    return

def get_results():
    if os.path.exists("results.csv"):
        log("Getting previous results from results file")
    return ""




#vote validation logic


def check_finland_name(name): #Returns false if person is a part of finland
    if name in finns:
        return False
    return True

def check_voted_name(name): #Returns false if person hasn't already voted
    if name not in voted_names:
        return False
    return True

def check_voted_ip(ip): #Returns false if an ip hasn't already voted
    if ip not in voted_ips:
        return False
    return True




#flask logic    

@app.errorhandler(404) #redirect all other pages to results
def go_to_results(e):
    return redirect("/results")

@app.route("/vote", methods=['GET', 'POST']) #voting page
def voting():

    if request.method == "GET":
        ordinals = [ordinal(i+1) for i in range(len(candidates))] #generate ordinals for all table rows
        return render_template("voting.html",ordinals=ordinals,candidates=candidates)
    else:
        data = request.json
        print(data)
        if len(data) == 0:
            log(request.remote_addr + " sent a post request with no data")
            return json.dumps({'success':False}), 418, {'ContentType':'application/json'}
        
        if check_voted_ip(request.remote_addr):
            log(request.remote_addr + " tried to vote twice, raw data: " + str(data))
            return json.dumps({'success':False,"message":"This IP has already been used to vote"}), 418, {'ContentType':'application/json'}

        print(request.remote_addr)
        username = data.get("voterName").lower()
        if check_voted_name(username):
            log(username + " tried to vote twice, this time with IP " + request.remote_addr + " raw data: "+ str(data))
            return json.dumps({'success':False,"message":"This username has already been used to vote"}), 418, {'ContentType':'application/json'}
        
        if check_finland_name(username):
            log(username + " tried to vote, but is not a part of Finland. IP: " + request.remote_addr + " raw data: "+ str(data))
            return json.dumps({'success':False,"message":"This username is not in a Finnish town"}), 418, {'ContentType':'application/json'} 
        
        
        voting_data = data.get("candidates")
        parsed_output = {}

        invalidated = False

        for i in voting_data:
            parsed_output[i["rank"]]=i["name"]
        
        if len(parsed_output) != len(candidates):
            invalidated = True
            
        for i in parsed_output.values():
            if i not in candidates:
                invalidated = True

        if invalidated:
            log("How did this happen? "+username+ " at IP" + request.remote_addr + " submitted broken data: " + str(parsed_output)) 
            return json.dumps({'success':False}), 418, {'ContentType':'application/json'}
        
        write_results(request.remote_addr,username,parsed_output)
        
        
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}



@app.route("/results") #results page
def results():
    return render_template("results.html")




#app startup

if __name__ == "__main__":
    start_logger()
    log("Reading listed candidates from candidates.txt")
    if not os.path.exists("candidates.txt"):
        log("candidates.txt file doesn't exist, exiting...");
        exit()
    with open("candidates.txt","r",encoding="UTF8") as file: #read participating candidates from candidates.txt and parse
        candidates = [i.replace("\n","") for i in file.readlines()] #remove line endings
        if len(candidates) == 0:
            log("no candidates listed, exiting...")
            exit()
        log("Listed candidates are: "+", ".join(candidates))
    log("Getting members in finland")
    try:
        finns = [i.lower() for i in requests.get("https://api.earthmc.net/v2/aurora/nations/Finland").json()["residents"]]
        log("Current members of the nation are: "+", ".join(finns))
    except:
        log("Something went wrong with getting nation members, exiting: "+traceback.format_exc())
        exit()
    log("Starting web application...")
    app.run()
    log("Application closed")
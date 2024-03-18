from flask import *
from datetime import datetime, timedelta
import os
import csv
import json
import requests

app = Flask(__name__)

candidates = []
voted_ips = []
voted_names = []
logfile = ""


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



#vote validation logic


def check_finland_name(name): #check whether voter is a part of finland
    names = requests.get("https://api.earthmc.net/v2/aurora/nations/Finland").json()["residents"]
    if name in names:
        return True
    return False

def check_voted_name(name):
    if name not in voted_names:
        return True
    return False

def check_voted_ip(ip):
    if ip not in voted_ips:
        return True
    return False
    

#flask logic    

@app.errorhandler(404) #redirect all other pages to results
def go_to_results(e):
    return redirect("/results")

@app.route("/vote", methods=['GET', 'POST']) #voting page
def voting():
    if request.method == "GET":
        #ordinal conversion oneliner, stolen from https://codegolf.stackexchange.com/questions/4707/outputting-ordinal-numbers-1st-2nd-3rd#answer-4712
        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4]) 
        ordinals = [ordinal(i+1) for i in range(len(candidates))] #generate ordinals for all table rows
        return render_template("voting.html",ordinals=ordinals,candidates=candidates)
    else:
        data = request.json
        print(data)
        if len(data) > 0:
            if check_voted_ip(request.remote_addr):
                username = data.get("voterName")
                if check_voted_name(username):
                    if check_finland_name(username):
                        votingdata = data.get("candidates")
                    else:
                        return "This username is not in a Finnish town"
                else:
                    return "This username has already been used to vote"
            else:
                return "This IP has already been used to vote"
        else:
            return "Invalid request"
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
    log("Starting web application...")
    app.run()
    log("Application closed")
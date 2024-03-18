from flask import *
from datetime import datetime, timedelta
import os

app = Flask(__name__)
candidates = []
logfile = ""


#logging logic

def start_logger():
    global logfile

    print("Initiating logger...")
    logfile = "log/"+datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3]+".txt"
    with open(logfile, "x") as file:
        file.write("-----------------------Log start-------------------------------\n")
    print("Logger initialized successfully");

def log(input): #we want to only log outputs from the actual voting site flask output, so I'm doing this'
    global logfile

    print(input)
    with open(logfile, "a") as file:
        file.write(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S ")+input+"\n")




#flask logic    

@app.errorhandler(404) #redirect all other pages to results
def go_to_results(e):
    return redirect("/results")

@app.route("/vote", methods=['GET', 'POST']) #voting page
def voting():
    return render_template("voting.html")

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
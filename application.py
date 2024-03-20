from flask import *
from datetime import datetime, timezone
from random import shuffle
from copy import deepcopy
import os
import json
import requests

app = Flask(__name__)

open_time = 1710972000 #1710885600 #voting open time (seconds since epoch)
close_time = 1711144800 #1711020720 #1710972000 #voting close time (seconds since epoch)

finns = [] #members in the nation of Finland, when the application is started
candidates = [] #candidates in the election
voted_ips = [] #IPs of people who already voted
voted_names = [] #usernames of people who already voted
ballots = {} #current ballot data
voting_results = {} #currently calculated results
logfile = "" #logfile location




#logging logic

def start_logger():
    global logfile
    
    print("Initializing logger...")
    if not os.path.exists("log"):
        print("Log directory not found, creating...")
        os.makedirs("log")
    logfile = "log/"+datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3]+".txt" #log file name is timestamped
    with open(logfile, "x") as file:
        file.write("-------------------------------Log start-------------------------------\n")
    print("Logger initialized successfully!")


def log(input): #we want to only log outputs from the actual voting site flask output, so I'm doing this'
    global logfile

    print(input)
    with open(logfile, "a") as file:
        file.write(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S ")+input+"\n")




#csv reading/writing logic

def file_setup():
    if not os.path.exists("results.csv"):
       log("Results file doesn't exist, creating...")
       with open("results.csv","x") as file:
           f_line="Timestamp,IP,voter name,"
           for i in range(len(candidates)):
               f_line+=ordinal(i+1)+" choice,"
           file.write(f_line+"\n")
       log("Results file creation successful!")

unwritten = [] #cannot write into csv file if it is open in excel, postpone for writing later
def write_results(ip,username,ballot):
    file_setup()
    data_to_write = [datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),ip,username]
    for i in ballot:
        data_to_write.append(i)
        
    removequeue = []
    try:
        log("Attempting to write current log data into file...")
        with open("results.csv","a") as file:    
            for i in unwritten: #postponed data
                log("Writing postponed vote: "+str(i)+" into file...")
                file.write(",".join(i)+"\n")    
                log("Success!")
                removequeue.append(i)
            log("Writing current vote into file...")
            file.write(",".join(data_to_write)+"\n")
        log("All votes written into file succesfully!")
        
    except:
        unwritten.append(data_to_write)
        log("Writing vote into file failed, postponing write...")
        log("Raw data: "+str(data_to_write))
        
    #remove postponed data from postponed data queue (I can't just clear unwritten, because it might fail mid-write and then some votes would get lost)
    for i in removequeue: 
        unwritten.remove(i)
    removequeue.clear()
    return


def get_previous_voters():
    if os.path.exists("results.csv"):
        log("Getting previous voters from results file...")
        with open("results.csv","r") as file:
            lines = file.readlines()
            for line in lines[1:]:
                splitLine = line.split(",")
                voted_ips.append(splitLine[1])
                voted_names.append(splitLine[2])
                log(splitLine[2]+" has already voted at IP "+splitLine[1])


def get_ballots():
    if os.path.exists("results.csv"):
        log("Getting results from file...")
        with open("results.csv","r") as file:
            lines = file.readlines()
            for line in lines[1:]:
                split_line = line.strip("\n").split(",")
                ballots[split_line[2]] = [split_line[i] for i in range(3,3+len(candidates))]
            log("Current ballots: "+str(ballots))
    return 




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




#utility thingies

#ordinal conversion oneliner, stolen from https://codegolf.stackexchange.com/questions/4707/outputting-ordinal-numbers-1st-2nd-3rd#answer-4712
ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])


def list_to_percentages(list):
    total = 0
    
    for i in list:
        total+=int(i)
    if total == 0:
        return ["0%" for i in list]
    else:
        return [str(int(int(i)/total*100))+"%" for i in list]


def calculate_results(): #returns whether winner is determined
#TODO fix the bit spaghet code
    log("Calculating current voting results...")
    removed = []
    losers = []
    votes = {}
    for i in candidates:
        votes[i] = [] #will contain players who voted as first choice (and then second chocie and etc)
    
    #round1
    for i in ballots:
        votes[ballots[i][0]].append(i)
    
    sorted_votes = dict(sorted(votes.items(), key=lambda item: len(item[1]))) #sorted candidates by votes
    min_votes = len(list(sorted_votes.values())[0])
    max_votes = len(list(sorted_votes.values())[-1])
    
    if min_votes == max_votes: #complete tie
        for i in candidates:
            voting_results[i] = min_votes
        log("Round 1 ends with a tie: "+str({i:len(votes[i]) for i in votes}))
        return False
    else:
        for i in votes:
            if len(votes[i]) == min_votes:
                voting_results[i] = min_votes
                losers.append(i)
        log("Round 1 voting results are: "+str({i:len(votes[i]) for i in votes})+" with the loser(s) being: "+", ".join(losers))
        for i in losers: #remove losers from counted votes, cause their final results already written
            if i in votes:
                del votes[i]
    
    removed = deepcopy(losers)
    losers.clear()
    
    if len(votes)==1:
        voting_results[list(votes)[0]] = max_votes
        return True
    
    #subsequent rounds
    round = 1
    running = True
    while running:
        for i in ballots:
            if ballots[i][round-1] in removed: #check if the previous, more preferrable choice has lost already
                if ballots[i][round] not in removed:
                    votes[ballots[i][round]].append(i)
        
        sorted_votes = dict(sorted(votes.items(), key=lambda item: len(item[1]))) #sorted candidates by votes
        min_votes = len(list(sorted_votes.values())[0])
        max_votes = len(list(sorted_votes.values())[-1])

        if min_votes == max_votes: #complete tie
            for i in candidates:
                voting_results[i] = min_votes
            log("Round "+str(round+1)+" ends with a tie: "+str({i:len(votes[i]) for i in votes}))
            return False
        else:
            for i in votes:
                if len(votes[i]) == min_votes:
                    voting_results[i] = min_votes
                    losers.append(i)
            log("Round "+str(round+1)+" voting results are: "+str({i:len(votes[i]) for i in votes})+" with the loser(s) being: "+", ".join(losers))
            for i in losers: #remove losers from counted votes, cause their final results already written
                if i in votes:
                    del votes[i]
        
        if len(votes)==1:
            voting_results[list(votes)[0]] = max_votes
            return True
        
        round+=1
        removed = deepcopy(losers)
        losers.clear()


def check_tie():
    sorted_results = dict(sorted(voting_results.items(), key=lambda item: item[1]))
    maxVotes = list(sorted_results.values())[-1]
    if list(sorted_results.values())[-2] == maxVotes:
        return True
    return False


def get_winner():
    return (sorted(voting_results.items(), key=lambda item: item[1]))[-1][0]


def is_open(): #if voting is open
    curr_time = int(datetime.now(timezone.utc).timestamp())
    if curr_time > open_time and curr_time < close_time:
        return True
    return False

def open_delta(): #get time delta to opening time or from opening time in seconds
    curr_time = int(datetime.now(timezone.utc).timestamp())
    if curr_time < open_time:
        return open_time-curr_time
    if curr_time > close_time: #will be negative to indicate that voting is closed
        return close_time-curr_time

def open_timestamp(): #returns either the timestamp when the voting opens or when it closes
    curr_time = int(datetime.now(timezone.utc).timestamp())
    if curr_time < open_time:
        return open_time
    if curr_time > close_time:
        return close_time
    return 0



#flask logic    

@app.errorhandler(404) #redirect all other pages to results
def go_to_results(e):
    return redirect("/results")


@app.route("/vote", methods=['GET', 'POST']) #voting page
def voting():
    if request.method == "GET":
        if is_open():
            ordinals = [ordinal(i+1) for i in range(len(candidates))] #generate ordinals for all table rows
            user_candidates = deepcopy(candidates) #so python won't create a pointer, but creates an actual separate list
            shuffle(user_candidates)
            voting_running = True
            timestamp = 0
        else:
            ordinals = []
            user_candidates = []
            voting_running = False
            timestamp = open_timestamp()*1000 #cause JS works with milliseconds
        return render_template("voting.html",ordinals = ordinals,candidates = user_candidates, running = voting_running, timestamp = timestamp)
    else:
        data = request.json
        if not is_open():
            log(request.remote_addr + " tried to vote, but voting isn't open yet")
            return json.dumps({"success":False,"message":"Voting is not currently open!"}), 418, {'ContentType':'application/json'}
        
        if len(data) == 0:
            log(request.remote_addr + " sent a post request with no data")
            return json.dumps({"success":False}), 418, {'ContentType':'application/json'}
        
        if check_voted_ip(request.remote_addr):
            log(request.remote_addr + " tried to vote twice, raw data: " + str(data))
            return json.dumps({"success":True,"message":"This IP has already been used to vote"}), 418, {'ContentType':'application/json'}

        username = data.get("voterName").lower()
        if check_voted_name(username):
            log(username + " tried to vote twice, this time at IP " + request.remote_addr + " raw data: "+ str(data))
            return json.dumps({"success":True,"message":"This username has already been used to vote"}), 418, {'ContentType':'application/json'}
        
        if check_finland_name(username):
            log(username + " tried to vote, but is not a part of Finland. IP: " + request.remote_addr + " raw data: "+ str(data))
            return json.dumps({"success":True,"message":"This username is not in a Finnish town"}), 418, {'ContentType':'application/json'}
        
        
        voting_data = data.get("candidates") #get ballot data from incoming json
        parsed_output = {}
        ballot = []

        invalidated = False

        for i in voting_data: #parse incoming data
            if i["name"] not in candidates: #if incorrect candidate
                invalidated = True
            parsed_output[i["rank"]]=i["name"]
        ballot = list(dict(sorted(parsed_output.items())).values()) #generate ballot from data
        
        if len(parsed_output) != len(candidates):
            invalidated = True

        if invalidated: #vote data is somehow broken
            log("How did this happen? "+username+ " at IP" + request.remote_addr + " submitted broken data: " + str(parsed_output)) 
            return json.dumps({"success":False}), 418, {'ContentType':'application/json'}
        
        write_results(request.remote_addr,username,ballot)
        
        voted_ips.append(request.remote_addr)
        voted_names.append(username)
        ballots[username] = ballot
        log(username+" has submitted their ballot: "+str(ballot))
        
        calculate_results()
        
        return json.dumps({"success":True,"message":"Your vote has been counted!"}), 200, {'ContentType':'application/json'}


@app.route("/results") #results page
def results():
    resulting_candidates = []
    vote_values = []
    
    for i in dict(sorted(voting_results.items(), key = lambda item: item[1], reverse = True)):
        resulting_candidates.append(i)
        vote_values.append(voting_results[i])
    
    percentages = list_to_percentages(vote_values)
    return render_template("results.html",candidates=resulting_candidates,results=vote_values, percentages=percentages)




#app startup

def init():
    global candidates
    global finns
    global voting_results
    start_logger()
    
    log("Reading listed candidates from candidates.txt...")
    if not os.path.exists("candidates.txt"):
        log("candidates.txt file doesn't exist, exiting...")
        exit()
    with open("candidates.txt","r",encoding="UTF8") as file: #read participating candidates from candidates.txt and parse
        candidates = [i.replace("\n","") for i in file.readlines()] #remove line endings
        if len(candidates) == 0:
            log("no candidates listed, exiting...")
            exit()
        log("Listed candidates are: "+", ".join(candidates))
    
    
    log("Getting members in Finland...")
    try:
        finns = [i.lower() for i in requests.get("https://api.earthmc.net/v2/aurora/nations/Finland").json()["residents"]]
        log("Current members of the nation are: "+", ".join(finns))
    except:
        log("Something went wrong with getting nation members: "+traceback.format_exc()+" exiting...")
        exit()
    
    #get data and calculate results
    get_previous_voters()
    get_ballots()
    calculate_results()
    
    #output current results
    if is_open():
        log("Voting is still open!")
        log("Current results are: "+str(voting_results))
        if check_tie():
            log("It's currently a tie!")
        else:
            log("The preliminary winner is "+get_winner()+"!")
    else:
        log("Voting is not open!")
    
    log("Starting webserver");
    
    


if __name__ == "__main__":
    init()
    app.run()
    log("Application closed...")
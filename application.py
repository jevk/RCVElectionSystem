from flask import *
from datetime import datetime, timezone
from random import shuffle
from copy import deepcopy
from hashlib import sha256
import os
import json
import requests
import traceback
import logging as pylogging

app = Flask(__name__)

open_time = 0 #voting open time (seconds since epoch)
close_time = 0 #voting close time (seconds since epoch)

finns = [] #members in the nation of Finland, when the application is started
candidates = [] #candidates in the election
voted_ips = [] #IPs of people who already voted
voted_names = [] #usernames of people who already voted
ballots = {} #current ballot data
voting_results = {} #currently calculated results
past_results = {} #past voting results - a dictionary of dictionaries
logfile = "" #logfile location

verbose = True




#logging logic

def start_logger(verb):
    global logfile
    global verbose
    
    if not verb:
        verbose = False

    
    if verbose: print("Initializing logger...")
    if not os.path.exists("log"):
        if verbose: print("Log directory not found, creating...")
        os.makedirs("log")
    logfile = "log/"+datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3]+".txt" #log file name is timestamped
    with open(logfile, "x") as file:
        file.write("-------------------------------Log start-------------------------------\n")
    if verbose: print("Logger initialized successfully!")


def log(input): #we want to only log outputs from the actual voting site flask output, so I'm doing this'
    global logfile
    curr_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S ")
    if verbose: 
        print(curr_time+"[VotingSite] "+input) #print output lookin like a minecraft server
    if os.path.exists(logfile):
        with open(logfile, "a") as file:
            file.write(curr_time+input+"\n")




#csv reading/writing logic

def file_setup():
    if not os.path.exists("results.csv"):
       log("Results file doesn't exist, creating...")
       with open("results.csv","x") as file:
           file.write("sep=,\n") #add separator character def to the start file so excel parses it correctly
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
            for line in lines[2:]:
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

def get_settings():
    global open_time
    global close_time
    global candidates
    
    log("Reading election settings from settings.json...")
    if not os.path.exists("settings.json"):
        log("settings.json file doesn't exist, exiting...")
        exit()

    with open("settings.json","r",encoding="UTF8") as file:
        data = json.loads("".join(file.readlines())) #load file contents into json
        
        open_time = data["open_time"]
        log("Election opening timestamp is: "+str(open_time))
        close_time = data["close_time"]
        log("Election closing timestamp is: "+str(close_time))
        
        candidates = data["candidates"]
        if len(candidates) == 0:
            log("No candidates listed, exiting...")
            exit()
        
        log("Listed candidates are: "+", ".join(candidates))


def get_finns():
    global finns

    log("Getting members in Finland...")
    try:
        #here's the API v2 implementation if you want to use that for some reason
        #finns = [i.lower() for i in requests.get("https://api.earthmc.net/v2/aurora/nations/Finland").json()["residents"]]
        
        #and here's the API v3 implementation
        raw_residents = requests.get("https://api.earthmc.net/v3/aurora/nations/?query=e08ba27e-7179-4b5b-b1b3-b15a117f7ae8").json()[0]["residents"]
        finns = [i["name"].lower() for i in raw_residents]
        log("Current members of the nation are: "+", ".join(finns))
    except:
        log("Something went wrong with getting nation members: "+traceback.format_exc()+" exiting...")
        exit()


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


def get_past_results():
    log("Getting past results...")
    elections = os.listdir("results")
    for i in elections:
        read_results = {}
        with open("results/"+i+"/results.txt","r") as file:
            for e in file.readlines():
                data = e.split(" - ")
                read_results[data[0]] = int(data[1].strip("\n"))
        
        past_results[i] = read_results    
    log("Success!")


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
        for i in votes:
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
    
    for i in losers:
        removed.append(i)
    
    if len(votes)==1:
        voting_results[list(votes)[0]] = max_votes
        return True
    
    #subsequent rounds
    round = 1
    running = True
    while running:
        for i in ballots:
            if ballots[i][0] in losers: #check if first choice was removed already
                for e in range(1,len(ballots[i])): #find next choice that is not eliminated already
                    if ballots[i][e] not in removed:
                        votes[ballots[i][e]].append(i)
                        break
        
        losers.clear()
        
        sorted_votes = dict(sorted(votes.items(), key=lambda item: len(item[1]))) #sorted candidates by votes
        min_votes = len(list(sorted_votes.values())[0])
        max_votes = len(list(sorted_votes.values())[-1])
        
        if min_votes == max_votes: #complete tie
            for i in votes:
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
        for i in losers:
            removed.append(i)


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


def open_timestamp(): #returns either the timestamp when the voting opens or when it closes
    curr_time = int(datetime.now(timezone.utc).timestamp())
    if curr_time < open_time:
        return open_time
    return close_time


def which_timestamp(): #returns which timestamp was returned
    curr_time = int(datetime.now(timezone.utc).timestamp())
    if curr_time < open_time:
        return "open"
    elif curr_time > close_time:
        return "close"
    return "running"




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
        else:
            ordinals = []
            user_candidates = []
        
        timestamp = open_timestamp()*1000 #cause JS works with milliseconds
        w_timestamp = which_timestamp() #which timestamp is given
        
        return render_template("voting.html",ordinals = ordinals,candidates = user_candidates, timestamp = timestamp, w_timestamp = w_timestamp, pagetitle = "Prime Minister Voting Sheet")
    else:
        data = request.json
        eyep = sha256(request.remote_addr.encode()).hexdigest()
        if not is_open():
            log(eyep + " tried to vote, but voting isn't open yet")
            return json.dumps({"success":False,"message":"Voting is not currently open!"}), 418, {'ContentType':'application/json'}
        
        if len(data) == 0:
            log(eyep + " sent a post request with no data")
            return json.dumps({"success":False}), 418, {'ContentType':'application/json'}
        
        if check_voted_ip(str(eyep)):
            log(eyep + " tried to vote twice, raw data: " + str(data))
            return json.dumps({"success":False,"message":"This IP has already been used to vote"}), 418, {'ContentType':'application/json'}

        username = data.get("voterName").lower()
        if check_voted_name(username):
            log(username + " tried to vote twice, this time at IP " + eyep + " raw data: "+ str(data))
            return json.dumps({"success":False,"message":"This username has already been used to vote"}), 418, {'ContentType':'application/json'}
        
        if check_finland_name(username):
            log(username + " tried to vote, but is not a part of Finland. IP: " + eyep + " raw data: "+ str(data))
            return json.dumps({"success":False,"message":"This username is not in a Finnish town"}), 418, {'ContentType':'application/json'}
        
        
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
            log("How did this happen? "+username+ " at IP" + eyep + " submitted broken data: " + str(parsed_output)) 
            return json.dumps({"success":False}), 418, {'ContentType':'application/json'}
        
        write_results(eyep,username,ballot)
        
        voted_ips.append(eyep)
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
    timestamp = open_timestamp()*1000 #cause JS works with milliseconds
    w_timestamp = which_timestamp() #which timestamp is given
    
    pagetitle = "Prime Minister Election Final Results"
    if w_timestamp != "close":
        pagetitle = "Prime Minister Election Preliminary Results"
    
    return render_template("results.html", candidates=resulting_candidates, results=vote_values, percentages=percentages, timestamp=timestamp, w_timestamp=w_timestamp, pagetitle=pagetitle)


@app.route("/past-elections") #past elections page
def past_elections():
    resulting_candidates = {}
    vote_values = {}
    percentages = {}
    
    for e in past_results:
        resulting_candidates[e] = []
        vote_values[e] = []
        for i in dict(sorted(past_results[e].items(), key = lambda item: item[1], reverse = True)):
            resulting_candidates[e].append(i)
            vote_values[e].append(past_results[e][i])
        percentages[e] = list_to_percentages(vote_values[e])
    
    return render_template("past-elections.html", pagetitle="Past Elections", candidates=resulting_candidates, results=vote_values, percentages=percentages)


@app.route("/tos") #terms of service page
def tos():
    return render_template("terms.html", pagetitle="Terms of Use and Privacy Policy")




#app startup

def init(verb = True):
    global candidates
    global finns
    global voting_results
    
    pylogging.getLogger('werkzeug').disabled = not verb
    
    start_logger(verb)
    get_past_results()
    get_settings()
    get_finns()
    
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




#for when testing

if __name__ == "__main__":
    init()
    app.run()
    log("Application closed...")
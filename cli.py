from waitress_server import run, application
from _thread import start_new_thread
from datetime import datetime



#commands

commands = {} #for help command functioning
def help_command(*args): #print help for all commands or a single command
    """View help info - syntax: 'help (command)'"""
    if len(args[0])>0:
        if args[0][0] in commands:
            if args[0][0] == "exit":
                print("exit - Exit the program")
            else:
                print(args[0][0],"-",commands[args[0][0]].__doc__)
        else:
            print("That command doesn't exist, to get a list of all the commands, type 'help'")
    else:
        for i in commands:
            if i == "exit":
                print("exit - Exit the program")
            else:
                print(i,"-",commands[i].__doc__)


def start_server(*args): #start the webserver (the webserver will close if the program closes)
    """Start the webserver"""
    start_new_thread(run,(False,))


def get_start(*args):
    """Get starting time of the election"""
    stamp = application.open_time
    print("Timestamp:",stamp,"Converted value:",datetime.fromtimestamp(stamp).strftime("%d-%m-%Y %H:%M:%S "))


def get_end(*args):
    """Get ending time of the election"""
    stamp = application.close_time
    print("Timestamp:",stamp,"Converted value:",datetime.fromtimestamp(stamp).strftime("%d-%m-%Y %H:%M:%S "))


def get_finns(*args):
    """Get currently stored finns on the running server, won't work if server isn't running"""
    print("Listed members of Finland:",application.finns)


def get_candidates(*args):
    """Get election candidates"""
    print("Candidates:",application.candidates)


def get_names(*args):
    """Get names of people who've already voted"""
    print("Players who have currently voted:",application.voted_names)


def get_ips(*args):
    """Get ip hashes of people who've already voted"""
    print("Ip hashses which have been used to vote:",application.voted_ips)
    
    
def get_ballots(*args):
    """Get currently submitted ballots"""
    print("Current ballots:\n","\n".join([i+": "+str(application.ballots[i]) for i in application.ballots]))
    
    
def get_results(*args):
    """Get currently calculated results"""
    print("Current results:",application.voting_results)




#init and mainloop logic

commands = {"exit":exit,
            "help":help_command,
            "start":start_server,
            "getstart":get_start,
            "getend":get_end,
            "getfinns":get_finns,
            "getcandidates":get_candidates,
            "getnames":get_names,
            "getips":get_ips,
            "getballots":get_ballots,
            "getresults":get_results,} #keyword:function
def main_loop():
    while True:
        a = input("> ")
        cmd = a.split()[0].lower() #idc about case sensitivity
        args = [i.lower() for i in a.split()[1:]] #still dno't care about case sensitivity
        
        if cmd not in commands:
            print("Invalid command, to get a list of all the commands, type 'help'")
        else:
            commands[cmd](args)

def init_console():
    print("===========================================================================")
    print("Welcome to the RCV-CLI!")
    print(len(commands),"commands available")
    print("To get a list of all the commands, type 'help'")
    print("Note: Some commands will not work when the webserver is ran outside the CLI")
    main_loop()

if __name__ == "__main__":
    init_console()
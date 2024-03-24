from waitress_server import run, application
from _thread import start_new_thread



#commands

commands = {} #for help command functioning
def help_command(*args): #print help for all commands or a single command
    """View help info"""
    for i in commands:
        if i == "exit":
            print("exit - Exit the program")
        else:
            print(i,"-",commands[i].__doc__)

def start_server(*args): #start the webserver (the webserver will close if the program closes)
    """Start the webserver"""
    start_new_thread(run,(False,))


#init and mainloop logic

commands = {"exit":exit,
            "help":help_command,
            "start":start_server} #keyword:function
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
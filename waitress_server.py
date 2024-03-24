from waitress import serve
import application
import logging

def run(verbose=True):
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
    
    application.init(verb=verbose)
    serve(application.app, host="0.0.0.0", port = 80) #oh no http, what if a hacker knows my geopolitical minecraft server votes
    application.log("Application closed...")

if __name__ == "__main__":
    run(verbose=True)
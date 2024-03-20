from waitress import serve
import application
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

application.init()
serve(application.app, host="0.0.0.0", port = 80) #oh no http, what if a hacker knows my geopolitical minecraft server votes
application.log("Application closed...")
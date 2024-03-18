from flask import *
import os
app = Flask(__name__)

@app.errorhandler(404)
def go_to_results(e):
    return redirect("/results")

@app.route("/vote") 
def voting():
    return render_template("voting.html")

@app.route("/results")
def results():
    return render_template("results.html")
if __name__ == "__main__":
    app.run()
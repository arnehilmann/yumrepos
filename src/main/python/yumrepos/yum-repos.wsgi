from flask import Flask
 
app = Flask(__name__)
 
@app.route("/")
def hello():
    return "Hello world!"
 
if __name__ == "__main__":
    app.run()


# import sys
# sys.path.insert(0, '/srv/http/yumrepos')
# from app import app as application

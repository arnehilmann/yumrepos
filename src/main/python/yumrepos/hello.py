from flask import Flask
 
app = Flask(__name__)
 
@app.route("/")
def hello():
    import os
    e = []
    for key, value in os.environ.items():
        e.append("%s: %s" % (key, value))
    return "Hello world!\n%s" % "\n".join(e)
 
if __name__ == "__main__":
    app.run()

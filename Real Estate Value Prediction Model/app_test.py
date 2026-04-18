from flask import Flask
print(">> app_test.py started")

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Flask is running ✅</h1>"

print(">> reached bottom of file, __name__ is", __name__)

if __name__ == "__main__":
    app.run(debug=True)

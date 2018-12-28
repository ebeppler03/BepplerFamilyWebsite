from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('homepage.html')

if __name__ == '__main__':
	print ("Test me")
	app.run(debug='true',host='0.0.0.0', port='80')

import requests
from flask import Flask, request
app = Flask(__name__)
 

@app.route('/square/submit', methods = ['POST'])
def square_submit():
   x = int(request.form.get('x', 0))

   ## simulate calling out to some Web service:
   ##
   r = requests.get('http://www.tavendo.com/')
   y = len(r.text)

   res = x * x + y
   return "{} squared plus {} is {}".format(x, y, res)



if __name__ == "__main__":
   app.run(debug = True)

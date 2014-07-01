from flask import Flask, request
app = Flask(__name__)
 

@app.route('/square/submit', methods = ['POST'])
def square_submit():
   x = int(request.form.get('x', 0))
   res = x * x
   return "{} squared is {}".format(x, res)
 

if __name__ == "__main__":
   app.run(port = 8080, debug = True)

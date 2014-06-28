from klein import run, route

@route('/')
def home(request):
   return 'wooooo'

@route('/<int:id>')
def id(request, id):
   return 'id is %d' % (id,)

@route('/hello/<string:name>')
def home(request, name = 'world'):
   return 'Got {}'.format(name)

run("localhost", 8080)

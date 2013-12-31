# Simple WAMP PubSub Load Test

For a full description, please see the blog post [here](http://tavendo.com/blog/post/autobahn-pi-benchmark/).

Run the load test server:

   pypy server.py

Get help for load test server:

   pypy server.py --help

Run the load test client:

   python client.py --wsuri ws://192.168.1.133:9000 --clients 500 --uprate 20 --rate 5 --batch 1 --payload 32

Get help for load test client:

   pypy client.py --help

test:
	PYTHONPATH=../../../../../autobahn python server.py

open:
	curl -H "Content-Type: application/json" \
	   -d '{"protocols": ["wamp.2.json"]}' \
	   http://127.0.0.1:8080/lp/open

receive:
	curl -H "Content-Type: application/json" -d "" \
	   http://127.0.0.1:8080/lp/kjmd3sBLOUnb3Fyr/receive

hello:
	curl -H "Content-Type: application/json" \
	   -d '[1, "realm1", {"roles": {"subscriber": {}, "publisher": {}}}]' \
	   http://127.0.0.1:8080/lp/kjmd3sBLOUnb3Fyr/send

subscribe:
	curl -H "Content-Type: application/json" \
	   -d '[32, 1, {}, "com.myapp.topic1"]' \
	   http://127.0.0.1:8080/lp/kjmd3sBLOUnb3Fyr/send

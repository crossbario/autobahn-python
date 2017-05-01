This shows how to use "retained" events as well as "event history".

The "backend.py" does some publishing to two different topics:
"com.example.history" and "com.example.no_history_here". The former
has event-history enabled (see the example router's config in the
"crossbardemo" realm).

When "frontend.py" attaches and subscribes to *either* of the two
topics, it will immediately receive the latest event.

After that, the WAMP Meta API is used to retrieve the event-history
from the "com.example.history" topic.

Things to try:

 - run backend.py, then run frontend.py in a new shell

 - run backend.py, kill it, then run frontend.py

 - with frontend.py running, kill and re-run backend.py several times

 - ...then try starting frontend.py again (which will show more events
   in the history

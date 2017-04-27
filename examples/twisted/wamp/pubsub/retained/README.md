This shows how to use "retained" events.

The "backend.py" will publish to 'event.foo' with "retain=True" option
turned on. This will cause the router to remember the event.

Now, when "frontend.py" attaches and subscribes to 'event.foo' with
"get_retained=True" option turned on, it will get the retained event
(even if the publisher session has already disconnected).

Try:

 - run backend.py, then run frontend.py in a new shell
 - run backend.py, kill it, then run frontend.py

# Custom Validation

WAMP is dynamically typed, which means, the application level payload of calls and events can be arbitrary, and the application components must be able to handle this.

Also, a WAMP router won't care at all about the application payload transported, other than converting between different serialization formats.

On the other hand, there are situations where we might want to impose some form of typing and validation to the application payloads.

The basic router `autobahn.wamp.router.Router` includes a `validate` hook to validate the application payload of calls, call results, call errors and published events.

To create a router that implements some form of payload validation, override the hook and throw exceptions whenever the payload does not conform.


## Example

Here is a custom router that will validate event publication to topic `com.myapp.topic1`. The payload of events published to that topic MUST BE a single positional integer, and that integer MUST BE even.

```python
from autobahn.wamp.exception import ApplicationError
from autobahn.wamp.router import Router

class MyRouter(Router):

   def validate(self, payload_type, uri, args, kwargs):
      if payload_type == 'event' and uri == 'com.myapp.topic1':
         if len(args) == 1 and type(args[0]) == int and args[0] % 2 == 0 and kwargs is None:
            return # ok, valid
         else:
            raise ApplicationError(ApplicationError.INVALID_ARGUMENT, "invalid event payload for topic {} - must be a single, even integer".format(uri))
```

> Note that payloads of different type (other than `event`) or any other URI are not validated here, but simply accepted.

To run this example, start the router

```sh
python router.py
```

and then start the client with an application component

```sh
python client.py
```


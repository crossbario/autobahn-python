# Code Review

 * `setTrackTimings`, `doTrack`



        App:  +------------------------+----------------------+
              |                        |
              |                        |
        Tap:  +-<-----<-----<-----<----+
        


# Monitor Tab

## Features
 * monitors an application's WAMP session
 * tracks RPC calls and PubSub Events
 * Start/Stop/Play Recording

## How it works

 * new browser tab opened from within an app tab via link
 * monitor tab URL points to a admin console location
 * monitor tab URL contains app key and WAMP session ID as URL query parameter
 * monitor JS connects to admin WAMP endpoint
 * admin WAMP endpoint checks for origin


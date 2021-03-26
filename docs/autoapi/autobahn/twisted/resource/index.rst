:mod:`autobahn.twisted.resource`
================================

.. py:module:: autobahn.twisted.resource


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.twisted.resource.WSGIRootResource
   autobahn.twisted.resource.WebSocketResource



.. class:: WSGIRootResource(wsgiResource, children)


   Bases: :class:`twisted.web.resource.Resource`

   Root resource when you want a WSGI resource be the default serving
   resource for a Twisted Web site, but have subpaths served by
   different resources.

   This is a hack needed since
   `twisted.web.wsgi.WSGIResource <http://twistedmatrix.com/documents/current/api/twisted.web.wsgi.WSGIResource.html>`_.
   does not provide a ``putChild()`` method.

   .. seealso::

      * `Autobahn Twisted Web WSGI example <https://github.com/crossbario/autobahn-python/tree/master/examples/twisted/websocket/echo_wsgi>`_
      * `Original hack <http://blog.vrplumber.com/index.php?/archives/2426-Making-your-Twisted-resources-a-url-sub-tree-of-your-WSGI-resource....html>`_

   .. method:: getChild(self, path, request)

      Retrieve a 'child' resource from me.

      Implement this to create dynamic resource generation -- resources which
      are always available may be registered with self.putChild().

      This will not be called if the class-level variable 'isLeaf' is set in
      your subclass; instead, the 'postpath' attribute of the request will be
      left as a list of the remaining path elements.

      For example, the URL /foo/bar/baz will normally be::

        | site.resource.getChild('foo').getChild('bar').getChild('baz').

      However, if the resource returned by 'bar' has isLeaf set to true, then
      the getChild call will never be made on it.

      Parameters and return value have the same meaning and requirements as
      those defined by L{IResource.getChildWithDefault}.



.. class:: WebSocketResource(factory)


   Bases: :class:`object`

   A Twisted Web resource for WebSocket.

   .. attribute:: isLeaf
      :annotation: = True

      

   .. method:: getChildWithDefault(self, name, request)

      This resource cannot have children, hence this will always fail.


   .. method:: putChild(self, path, child)

      This resource cannot have children, hence this is always ignored.


   .. method:: render(self, request)

      Render the resource. This will takeover the transport underlying
      the request, create a :class:`autobahn.twisted.websocket.WebSocketServerProtocol`
      and let that do any subsequent communication.




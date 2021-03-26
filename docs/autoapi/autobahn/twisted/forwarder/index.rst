:mod:`autobahn.twisted.forwarder`
=================================

.. py:module:: autobahn.twisted.forwarder


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   autobahn.twisted.forwarder.DestEndpointForwardingProtocol
   autobahn.twisted.forwarder.DestEndpointForwardingFactory
   autobahn.twisted.forwarder.EndpointForwardingProtocol
   autobahn.twisted.forwarder.EndpointForwardingService
   autobahn.twisted.forwarder.Options



Functions
~~~~~~~~~

.. autoapisummary::

   autobahn.twisted.forwarder.makeService


.. class:: DestEndpointForwardingProtocol

   Bases: :class:`twisted.internet.protocol.Protocol`

   This is the base class for streaming connection-oriented protocols.

   If you are going to write a new connection-oriented protocol for Twisted,
   start here.  Any protocol implementation, either client or server, should
   be a subclass of this class.

   The API is quite simple.  Implement L{dataReceived} to handle both
   event-based and synchronous input; output can be sent through the
   'transport' attribute, which is to be an instance that implements
   L{twisted.internet.interfaces.ITransport}.  Override C{connectionLost} to be
   notified when the connection ends.

   Some subclasses exist already to help you write common types of protocols:
   see the L{twisted.protocols.basic} module for a few of them.

   .. attribute:: log
      

      

   .. method:: connectionMade(self)

      Called when a connection is made.

      This may be considered the initializer of the protocol, because
      it is called when the connection is completed.  For clients,
      this is called once the connection to the server has been
      established; for servers, this is called after an accept() call
      stops blocking and a socket has been received.  If you need to
      send any greeting or initial message, do it here.


   .. method:: dataReceived(self, data)

      Called whenever data is received.

      Use this method to translate to a higher-level message.  Usually, some
      callback will be made upon the receipt of each complete protocol
      message.

      @param data: a string of indeterminate length.  Please keep in mind
          that you will probably need to buffer some data, as partial
          (or multiple) protocol messages may be received!  I recommend
          that unit tests for protocols call through to this method with
          differing chunk sizes, down to one byte at a time.


   .. method:: connectionLost(self, reason)

      Called when the connection is shut down.

      Clear any circular references here, and any external references
      to this Protocol.  The connection has been closed.

      @type reason: L{twisted.python.failure.Failure}



.. class:: DestEndpointForwardingFactory(sourceProtocol)


   Bases: :class:`twisted.internet.protocol.Factory`

   This is a factory which produces protocols.

   By default, buildProtocol will create a protocol of the class given in
   self.protocol.

   .. method:: buildProtocol(self, addr)

      Create an instance of a subclass of Protocol.

      The returned instance will handle input on an incoming server
      connection, and an attribute "factory" pointing to the creating
      factory.

      Alternatively, L{None} may be returned to immediately close the
      new connection.

      Override this method to alter how Protocol instances get created.

      @param addr: an object implementing L{twisted.internet.interfaces.IAddress}



.. class:: EndpointForwardingProtocol

   Bases: :class:`twisted.internet.protocol.Protocol`

   This is the base class for streaming connection-oriented protocols.

   If you are going to write a new connection-oriented protocol for Twisted,
   start here.  Any protocol implementation, either client or server, should
   be a subclass of this class.

   The API is quite simple.  Implement L{dataReceived} to handle both
   event-based and synchronous input; output can be sent through the
   'transport' attribute, which is to be an instance that implements
   L{twisted.internet.interfaces.ITransport}.  Override C{connectionLost} to be
   notified when the connection ends.

   Some subclasses exist already to help you write common types of protocols:
   see the L{twisted.protocols.basic} module for a few of them.

   .. attribute:: log
      

      

   .. method:: connectionMade(self)

      Called when a connection is made.

      This may be considered the initializer of the protocol, because
      it is called when the connection is completed.  For clients,
      this is called once the connection to the server has been
      established; for servers, this is called after an accept() call
      stops blocking and a socket has been received.  If you need to
      send any greeting or initial message, do it here.


   .. method:: dataReceived(self, data)

      Called whenever data is received.

      Use this method to translate to a higher-level message.  Usually, some
      callback will be made upon the receipt of each complete protocol
      message.

      @param data: a string of indeterminate length.  Please keep in mind
          that you will probably need to buffer some data, as partial
          (or multiple) protocol messages may be received!  I recommend
          that unit tests for protocols call through to this method with
          differing chunk sizes, down to one byte at a time.


   .. method:: connectionLost(self, reason)

      Called when the connection is shut down.

      Clear any circular references here, and any external references
      to this Protocol.  The connection has been closed.

      @type reason: L{twisted.python.failure.Failure}



.. class:: EndpointForwardingService(endpointDescriptor, destEndpointDescriptor, reactor=None)


   Bases: :class:`twisted.application.service.Service`

   Base class for services.

   Most services should inherit from this class. It handles the
   book-keeping responsibilities of starting and stopping, as well
   as not serializing this book-keeping information.

   .. method:: startService(self)


   .. method:: stopService(self)



.. class:: Options


   Bases: :class:`twisted.python.usage.Options`

   An option list parser class

   C{optFlags} and C{optParameters} are lists of available parameters
   which your program can handle. The difference between the two
   is the 'flags' have an on(1) or off(0) state (off by default)
   whereas 'parameters' have an assigned value, with an optional
   default. (Compare '--verbose' and '--verbosity=2')

   optFlags is assigned a list of lists. Each list represents
   a flag parameter, as so::

      optFlags = [['verbose', 'v', 'Makes it tell you what it doing.'],
                  ['quiet', 'q', 'Be vewy vewy quiet.']]

   As you can see, the first item is the long option name
   (prefixed with '--' on the command line), followed by the
   short option name (prefixed with '-'), and the description.
   The description is used for the built-in handling of the
   --help switch, which prints a usage summary.

   C{optParameters} is much the same, except the list also contains
   a default value::

      optParameters = [['outfile', 'O', 'outfile.log', 'Description...']]

   A coerce function can also be specified as the last element: it will be
   called with the argument and should return the value that will be stored
   for the option. This function can have a C{coerceDoc} attribute which
   will be appended to the documentation of the option.

   subCommands is a list of 4-tuples of (command name, command shortcut,
   parser class, documentation).  If the first non-option argument found is
   one of the given command names, an instance of the given parser class is
   instantiated and given the remainder of the arguments to parse and
   self.opts[command] is set to the command name.  For example::

      subCommands = [
           ['inquisition', 'inquest', InquisitionOptions,
                'Perform an inquisition'],
           ['holyquest', 'quest', HolyQuestOptions,
                'Embark upon a holy quest']
       ]

   In this case, C{"<program> holyquest --horseback --for-grail"} will cause
   C{HolyQuestOptions} to be instantiated and asked to parse
   C{['--horseback', '--for-grail']}.  Currently, only the first sub-command
   is parsed, and all options following it are passed to its parser.  If a
   subcommand is found, the subCommand attribute is set to its name and the
   subOptions attribute is set to the Option instance that parses the
   remaining options. If a subcommand is not given to parseOptions,
   the subCommand attribute will be None. You can also mark one of
   the subCommands to be the default::

      defaultSubCommand = 'holyquest'

   In this case, the subCommand attribute will never be None, and
   the subOptions attribute will always be set.

   If you want to handle your own options, define a method named
   C{opt_paramname} that takes C{(self, option)} as arguments. C{option}
   will be whatever immediately follows the parameter on the
   command line. Options fully supports the mapping interface, so you
   can do things like C{'self["option"] = val'} in these methods.

   Shell tab-completion is supported by this class, for zsh only at present.
   Zsh ships with a stub file ("completion function") which, for Twisted
   commands, performs tab-completion on-the-fly using the support provided
   by this class. The stub file lives in our tree at
   C{twisted/python/twisted-completion.zsh}, and in the Zsh tree at
   C{Completion/Unix/Command/_twisted}.

   Tab-completion is based upon the contents of the optFlags and optParameters
   lists. And, optionally, additional metadata may be provided by assigning a
   special attribute, C{compData}, which should be an instance of
   C{Completions}. See that class for details of what can and should be
   included - and see the howto for additional help using these features -
   including how third-parties may take advantage of tab-completion for their
   own commands.

   Advanced functionality is covered in the howto documentation,
   available at
   U{http://twistedmatrix.com/projects/core/documentation/howto/options.html},
   or doc/core/howto/options.xhtml in your Twisted directory.

   .. attribute:: synopsis
      :annotation: = [options]

      

   .. attribute:: longdesc
      :annotation: = Endpoint Forwarder.

      

   .. attribute:: optParameters
      :annotation: = [['endpoint', 'e', None, 'Source endpoint.'], ['dest_endpoint', 'd', None, 'Destination endpoint.']]

      


.. function:: makeService(config)



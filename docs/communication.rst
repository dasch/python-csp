
Communication
=============


Channels
--------

Channels are the main means of communication between processes. They provide
bidirectional exchange of messages.

Multiple processes can read and write to the same channel, but only one
can write, and another read, at any one time.


.. autoclass:: csp.Channel

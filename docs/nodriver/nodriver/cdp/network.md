# Network

Network domain allows tracking network activities of the page. It exposes information about http, file, data and other requests and responses, their headers, bodies, timing, etc.

  * [Types](#types)

  * [Commands](#commands)

  * [Events](#events)




# Types

Generally, you do not need to instantiate CDP types yourself. Instead, the API creates objects for you as return values from commands, and then you can use those objects as arguments to other commands.

# Commands

Each command is a generator function. The return type Generator[x, y, z] indicates that the generator _yields_ arguments of type x, it must be resumed with an argument of type y, and it returns type z. In this library, types x and y are the same for all commands, and z is the return type you should pay attention to. For more information, see :ref:`Getting Started: Commands <getting-started-commands>`.

# Events

Generally, you do not need to instantiate CDP events yourself. Instead, the API creates events for you and then you use the event's attributes.

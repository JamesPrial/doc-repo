# Inspector

_This CDP domain is experimental._

  * [Types](#types)

  * [Commands](#commands)

  * [Events](#events)




# Types

_There are no types in this module._

# Commands

Each command is a generator function. The return type Generator[x, y, z] indicates that the generator _yields_ arguments of type x, it must be resumed with an argument of type y, and it returns type z. In this library, types x and y are the same for all commands, and z is the return type you should pay attention to. For more information, see :ref:`Getting Started: Commands <getting-started-commands>`.

# Events

Generally, you do not need to instantiate CDP events yourself. Instead, the API creates events for you and then you use the event's attributes.

# Runtime

Runtime domain exposes JavaScript runtime by means of remote evaluation and mirror objects. Evaluation results are returned as mirror object that expose object type, string representation and unique identifier that can be used for further object reference. Original objects are maintained in memory unless they are either explicitly released or are released along with the other objects in their object group.

  * [Types](#types)

  * [Commands](#commands)

  * [Events](#events)




# Types

Generally, you do not need to instantiate CDP types yourself. Instead, the API creates objects for you as return values from commands, and then you can use those objects as arguments to other commands.

# Commands

Each command is a generator function. The return type Generator[x, y, z] indicates that the generator _yields_ arguments of type x, it must be resumed with an argument of type y, and it returns type z. In this library, types x and y are the same for all commands, and z is the return type you should pay attention to. For more information, see :ref:`Getting Started: Commands <getting-started-commands>`.

# Events

Generally, you do not need to instantiate CDP events yourself. Instead, the API creates events for you and then you use the event's attributes.

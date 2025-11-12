# CSS

This domain exposes CSS read/write operations. All CSS objects (stylesheets, rules, and styles) have an associated id used in subsequent operations on the related object. Each object type has a specific id structure, and those are not interchangeable between objects of different kinds. CSS objects can be loaded using the get*ForNode() calls (which accept a DOM node id). A client can also keep track of stylesheets via the styleSheetAdded/styleSheetRemoved events and subsequently load the required stylesheet contents using the getStyleSheet[Text]() methods.

_This CDP domain is experimental._

  * [Types](#types)

  * [Commands](#commands)

  * [Events](#events)




# Types

Generally, you do not need to instantiate CDP types yourself. Instead, the API creates objects for you as return values from commands, and then you can use those objects as arguments to other commands.

# Commands

Each command is a generator function. The return type Generator[x, y, z] indicates that the generator _yields_ arguments of type x, it must be resumed with an argument of type y, and it returns type z. In this library, types x and y are the same for all commands, and z is the return type you should pay attention to. For more information, see :ref:`Getting Started: Commands <getting-started-commands>`.

# Events

Generally, you do not need to instantiate CDP events yourself. Instead, the API creates events for you and then you use the event's attributes.

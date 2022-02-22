# Sonica WebSocket Gateway

## Format
The format of all messages is the outer object:

```scala
{ channel: Int64, type: String, value: Map<String, Any> }
```

The token is like a channel, and chosen by the initiating party, and used for all communication.
A simple call could be the client calling with:

```scala
{ channel: 152, type: "Play", value: {} }
```

to which the server might then respond:

```scala
{ channel: 152, type: "Finish", value: {} }
```

or it could return:

```scala
{ channel: 152, type: "Error", value: { message: "Nothing in library" } }
```


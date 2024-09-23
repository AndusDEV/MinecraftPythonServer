# Minecraft Server Implementation in Python
This is my take on creating a (partial) implementation of the Minecraft Protocol in Python to allow clients for connecting with it.

> [!NOTE]
> This won't be a full Minecraft Vanilla reimplementation. It's just a fun side-project to see how far can I take it.

## What works now:
- [ ] Server List:
  - [x] Server Description
  - [x] (Fake) Minimum/Maximum Players
  - [ ] Ping (ms)
    - Shows "Pinging..." forever
- [ ] Connecting to the server:
  - [x] Getting Player State (HANDSHAKE, STATUS, LOGIN, etc.)
  - [x] When player joins a server, they're immediately kicked
    - This will be later turned into a command
  - [ ] Spawning player in a blank/void world _(or flat)_
  - [ ] Working chat
  - [ ] Announcing that the player joined on chat
- [ ] Other things:
  - [ ] /kick command:
    - Kicks the player which used it
  - [ ] /msg command:
    - Sends a message from one player to another
    - Example: `/msg Player2 Hi!`
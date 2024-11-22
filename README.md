![Test](illustrations/test.svg) ![Coverage](illustrations/coverage.svg) ![Performance](illustrations/performance.svg)

# Digital Simulator

A program to design and simulate digital circuits

The idea is to create something akin to [Digital](https://github.com/hneemann/Digital) although less ambitious.

We will not implement it in Java, but in Python and use the [PyGame](https://github.com/pygame/pygame) package to render the graphical user interface. Because we use [Pygame-gui](https://github.com/MyreMylar/pygame_gui) for user interface elements like buttons and file dialogs, we will actually use the [Pygame-ce fork](https://github.com/pygame-community/pygame-ce) because pygame-gui has a hard dependency on that and will install it automatically, but that makes no difference to the functionality. I don't see any real advantage of using pygame-ce, but its development does indeed seem to be more active.

## project goals

This project is not so much about digital simulations per se, but more about learning some more about a few interesting pieces of technology:

- gain some experience with pygame

  pygame appears to be quite fast and flexible, albeit it little low level. However, this should enable us to create both a menu elements like buttons, as well as other graphical elements like representations of logical gates that change their appearance according to the state the get during a simulation
  
- gain some experience with pyinstaller 

  The promise of [pyinstaller](https://github.com/pyinstaller/pyinstaller) is that it will be able to create a single executable out of our collection of Python modules will the dependencies bundled inside it.
  I have never done that before, but because this makes it really easy to distribute the program, it is an interesting subject to test.

- a proper test framework

  At the very least for all logical components and simulation related stuff. Not sure how we could create a good test framework for the interaction though; we'd have tot hink about that one.
  
## design goals

Besides the project goals there are of course some technical goals we would like to reach to make the program at least a little bit useful:

- [ ] simulate all common gates

And, Or, Xor, Nand, Nor, NXor, along with some helper elements like an input that can be toggled, and lines to connect components.
      
- [ ] save and load designs

probably as JSON data, but pickling might be an option too.
      
- [ ] group elements into reusable blocks and add them to a library

this would make it possible to build and expand upon a collection of components of increasing complexity. Think latches, flip-flops, adders, ... etc.
      
- [ ] load/add to a library

Might be as simple as having the library as part of a saved design, so that an empty design can act as a library file.
      
- [ ] add clock input element

Slightly more complicated than an inout element that can be toggled on or off, but would make the simulation a lot more interesting.
      
- [ ] bundle the whole program into a single executable

pyinstaller is the first choice, but nothing is set in stone.
      
- [ ] have a proper test framework for the logic

pytest with the coverage and perhaps the performance add-ons should do the job, but the challenge here is to get good coverage. It is not at all clear to me if we can properly test pygame related functionality.

- [ ] nice to have: busses and nets

i.e. ways to label connectors and have them interact in a simulation as well as being able to define Line elements with multiple traces.

## current performance

![Performance graph](illustrations/simulation_benchmark.png)
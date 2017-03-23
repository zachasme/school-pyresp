# 02148 - A tuple space API implemented in Python

## How-to
While developing the API, we have made a couple of programs for testing the
features of our API. Below you will find instructions on how to run these
tests. We have supplied a make file for ease of use. The applications have
been tested to work with the following software versions:

- Python 3.6.0
- OpenJDK 1.8.0_122
- GNU Make 4.2.1

Feel free to inspect the accompanying `Makefile` for all available targets.

### Running the unit test suite from the development process
The unit test suite can be run by executing `make test`. Note that this
requires the python module `pytest`, which can be installed using

    pip install pytest

Make sure one uses `pip3` and not `pip2`.

### Running the benmcharking tools
+ To compare the python and java implementations use `make benchmark-python`
  and `make benchmark-java` respectively.
+ To compare the python tuple space implementations use `make benchmark-ts`

### Running the RemotePingPong example
+ In one terminal, while in the root directory run `make runpong` to run the
	jRESP Pong program. The target `runpong-debug` enables logging of JSON
	objects sent by jRESP.
+ Open another terminal. In the root directory run `make runping` to run the
	pyRESP Ping program.

### Running the RemoteEvaluation example (Cloud factorial computation)
+ Open a terminal. Navigate to the root directory. Run `make reval-server` to
	start up the server application. The target `reval-debug` runs a debugging
	server that prints all the JSON strings that it sends over the network.
+ Open up a second terminal. Navigate to the root directory and run
	`make reval-client` to run the Python client which will connect to the
	server and request a series of factorial computations.

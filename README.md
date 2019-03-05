# pyDist
pyDist allows users to simply and efficiently
distribute python functions or scripts to computers on the
same network. In the future pyDist will also allow for
communication between processes similar to that of mpi, but
a much simpler interface will be used and objects will be
passed as messages. The ultimate goal is to allow seamless 
integration with Python3's Futures standard. This way users
who are unfamiliar with parallel computing can still write
code to be run on a large scale.

```diff
- Only tested on Linux with python 3.6! I know it doesn't
- work on MAC so don't even try it :)
``` 

## TODO
* A user should be able to specify a code directory that will be
saved on all nodes in the network. This will allow users to execute
more complicated functions other than those defined in `__main__`.

## Setting up Your Virtual Environment
To develop for pyDist you will need to first create a Python virtual
environment that contains all the necessary dependencies required by
the core code. Essentially this virtual environment includes a
python installation that is separate from the default python 
installation on your computer.

To create the virtual environment you first need to
change directory into the pyDist repository (not the pyDist package)
and execute the following command.
```
make build_env
```
This will setup your virtual environment named `distEnv` using an
existing python3 installation. Note that this is being developed 
for linux so if you are on Windows good luck. Then you can activate 
your environment using
```
source distEnv/bin/activate
```
and deactivate the virtual environment using
```
deactivate
```
when the environment is no longer needed. 

Link to docs on Python virtual environments: 
<https://packaging.python.org/guides/installing-using-pip-and-virtualenv/>.

## Setup a Simple Cluster
To setup a very basic cluster we will simply start two nodes on
this machine. So instead of working with multiple computers we 
will only work with the current computer you are working on. All you
will need to know is your computers ip address given out by your 
router. It is very important that you use `192.168.0.XXX` for example
instead of `127.0.0.1` because when you decide to connect other computers
together you will need to know the ip address given out by your
router anyways. 

From the base directory of this repo call
```
python tests/spawn.py 4 192.168.0.XXX 9000
```
This line of code will start a master node at port 9000 on your computer.
The next line of code will setup another node on your computer, but
this time the node will connect to the master node. You will need to 
run the next command in another terminal
```
python tests/spawn.py 4 192.168.0.XXX 9001 192.168.0.XXX 9000
```
At this point we have a master node with a child node connected to it. 
And to test the network we call an example script in another terminal window
which sends a few tasks to the network for execution
```
python tests/sendTasks.py 192.168.0.XXX 9000
```
Notice that this script is connecting to the head node not the child
node. If all is working well you should start to see output in all 
three terminal windows.

One quick note: you can connect both of these nodes to each other, but
at this point that functionality would lead to issues when tasks are sent
to either node. The tasks would bounch back and forth between the two nodes
causing a slowdown in the network. This is because tasks can move anywhere in
the network an infinite number of times. A hop count is needed to fix this (
similar to a ip packet's hop count limit). For now restrict your network
structures to something resembling a tree.


## Running Tests
To run all tests on your local computer you can run the command
```
make test
```
from the base directory of the project. This will take up to 
several minutes to run all tests. Each of these tests will create
its own instance of the node server several times throughout the 
testing process which is why the code takes so long to execute.

## Known Issues

* The python package psutil requires that python header files be installed
on your computer. So you need to run `sudo apt-get install python-dev` to install
these header files. Then you can run the make command to build your environment
again.

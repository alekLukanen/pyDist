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



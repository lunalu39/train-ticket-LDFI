
# ZL-LDFI with Train Ticket

We implemented ZL-LDFI, an improved version of LDFI technique, to automate failure testing for the microservice based applications. Our evaluation uses Train Ticket system, you may find detailed description in train ticket folder. For this project, we edited train ticket original code about verification and redirect deployment file to our image repository. 

ZL LDFI requires to deploy train ticket with istio and install Jaeger as tool.

## LDFI folder

This folder contains our core algorithm. 

algo.py has LDFI, priority and pruning strategies. 

util.py has utility functions involving istio fault injection, Jaeger traces extraction and retrieval from Jaeger based on request type(s).

jmeter folder contains jmeter souce code which is the version we use. jmeter_code folder has our detailed implementation of 9 request types.

 

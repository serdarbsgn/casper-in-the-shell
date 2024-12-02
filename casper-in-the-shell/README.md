# Casper in the Shell

Api for storing and retrieving commands & Helper script for easier use.

## About

Written in python/fastapi, openapi descriptions are sufficient enough for MVP.

For openapi documentation:
```sh
http://localhost:8002/docs
```    

For plaintext explanations about endpoints:
```sh
http://localhost:8002/
```    
## Build & Usage

Build the container.
```sh
docker-compose up --build
```    

After building the container, **I highly recommend you use cins.py to interact with the api**, but you could definitely use it as is as well.
Requires Python3 on your system.

You could 
```sh
chmod +x cins.py
``` 

You can see the commands and what do they do by typing this.
```sh 
./cins.py -h
 ```
It does create a file '/tmp/cins_jwt' to store user token and use it for authentication.


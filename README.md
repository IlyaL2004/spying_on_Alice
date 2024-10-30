# spying_on_Alice

## Follow this tips to run the container

1. move to the folder where the Dockerfile is
2. run in terminal `docker build -t model .` or `docker build -t model . -f- <Dockerfile` if the deamon doesn't see the dockerfile 
3. wait about 2-4 min for image (maybe brew some coffee)
4. get your container by running `docker run --rm -it -p 80:80 model`

After this actions (if all goes fine) you can go to http://127.0.0.1/docs and try the model by loading users report in .csv format

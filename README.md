# MAX Image Caption Generator Web App

A demo web app for MAX using the Image Caption Generator model

### Before Starting the Web App

Before starting this web app you must setup the MAX Image Caption Generator REST endpoint by following the README here:

https://github.com/IBM/MAX-Image-Caption-Generator

You need to have the Image Caption Generator REST endpoint running at `http://localhost:5000` for the web app to run.

### Starting the Web App

Before running this web app you must install it's dependencies:

    pip install requests tornado

You then start the web app by running:

    python app.py

### Instructions for Docker

To run the web app with Docker you need to allow the containers running the web
server and the REST endpoint to share the same network stack. This is done in
the following steps.

Modify the command that runs the Image Caption Generator REST endpoint
to map the 8088 port:

    docker run -it -p 5000:5000 -p 8088:8088 --name max-im2txt max-im2txt


Build the web app image by running:

    docker build -t webapp .

Run the web app container using:

    docker run --net='container:max-im2txt' -it webapp


### JavaScript Libraries

This web app depends on a couple of non-standard js libraries

- [Image Picker](http://rvera.github.io/image-picker/)
- [d3 word cloud](https://github.com/jasondavies/d3-cloud)

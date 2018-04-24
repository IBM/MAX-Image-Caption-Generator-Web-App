# MAX Image Caption Generator Web App

A demo web app for MAX using the Image Caption Generator model

## Before Starting the Web App

Before starting this web app you must setup the MAX Image Caption Generator REST endpoint by following the README at:

[MAX Image Caption Generator GitHub](https://github.com/IBM/MAX-Image-Caption-Generator)

## Starting the Web App

Before running this web app you must install it's dependencies:

    pip install requests tornado

You then start the web app by running:

    python app.py

Once it's finished processing the default images (< 1 minute) you can then access the web app at: 
[http://localhost:8088](http://localhost:8088)

The Image Caption Generator endpoint must be available at `http://localhost:5000` for the web app to successfully start.

If you want to use a different port or are running the ML endpoint at a different location
you can change them with command-line options:

    python app.py --port=[new port] --ml-endpoint=[endpoint url including protocol and port]

## Instructions for Docker

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

## JavaScript Libraries

This web app includes the following js and css libraries

- [Image Picker](http://rvera.github.io/image-picker/)
- [d3-cloud](https://github.com/jasondavies/d3-cloud)
- [D3.js](https://d3js.org)
- [Bootstrap 3](https://getbootstrap.com)
- [JQuery](https://jquery.com)

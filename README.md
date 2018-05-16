# Use a deep learning model to filter images in a web application

Every day 2.5 quintillion bytes of data are created, based on an [IBM study](https://public.dhe.ibm.com/common/ssi/ecm/wr/en/wrl12345usen/watson-customer-engagement-watson-marketing-wr-other-papers-and-reports-wrl12345usen-20170719.pdf). A lot of that data is unstructured data,
such as large texts, audio recordings, and images. In order to do something useful
with the data, we must first convert it to structured data.

In this Code Pattern we will use one of the models from the [Model Asset Exchange](https://developer.ibm.com/code/exchanges/models/),
an exchange where developers can find and experiment with open source deep learning
models. Specifically we will be using the [Image Caption Generator](https://github.com/IBM/MAX-Image-Caption-Generator)
to create a web application that will caption images and allow the user to filter through
images based image content. The web application provides an interactive user interface
backed by a lightweight python server using Tornado. The server takes in images via the
UI and sends them to a REST end point for the model and displays the generated
captions on the UI. The model's REST endpoint is set up using the docker image
provided on MAX. The Web UI displays the generated captions for each image as well
as an interactive word cloud to filter images based on their caption.

When the reader has completed this Code Pattern, they will understand how to:

* Build a Docker image of the Image Caption Generator MAX Model
* Deploy a deep learning model with a REST endpoint
* Generate captions for an image using the MAX Model's REST API
* Run a web application that using the model's REST API


# Steps

## Setting up the MAX Model

Note: The set of instructions in this section are a modified version of the one found on the [Image Caption Generator Project Page](https://github.com/IBM/MAX-Image-Caption-Generator)

### 1. Build the Model

Clone the Image Caption Generator model locally. In a terminal, run the following command:

    git clone https://github.com/IBM/MAX-Image-Caption-Generator.git

Change directory into the repository base folder:

    cd MAX-Image-Caption-Generator

To build the docker image locally, run:

    docker build -t max-im2txt .

All required model assets will be downloaded during the build process. _Note_ that currently this docker image is CPU only (we will add support for GPU images later).

### 2. Deploy the Model

To run the docker image, which automatically starts the model serving API, run:


    docker run -it -p 5000:5000 max-im2txt


### 3. Experimenting with the API (Optional)

The API server automatically generates an interactive Swagger documentation page. Go to `http://localhost:5000` to load it. From there you can explore the API and also create test requests.

Use the `model/predict` endpoint to load a test file and get captions for the image from the API.

You can also test it on the command line, for example:


    curl -F "image=@assets/surfing.jpg" -X POST http://localhost:5000/model/predict


```json
{
  "status": "ok",
  "predictions": [
    {
      "index": "0",
      "caption": "a man riding a wave on top of a surfboard .",
      "probability": 0.038827644239537
    },
    {
      "index": "1",
      "caption": "a person riding a surf board on a wave",
      "probability": 0.017933410519265
    },
    {
      "index": "2",
      "caption": "a man riding a wave on a surfboard in the ocean .",
      "probability": 0.0056628732021868
    }
  ]
}
```

## Starting the Web App

### 1. Installing dependencies and running the server

Before running this web app you must install its dependencies:

    pip install requests tornado

You then start the web app by running:

    python app.py

Once it's finished processing the default images (< 1 minute) you can then access the web app at:
[http://localhost:8088](http://localhost:8088)

The Image Caption Generator endpoint must be available at `http://localhost:5000` for the web app to successfully start.

![Web UI Screenshot](assets/webui.png)

### Configuring ports (Optional)

If you want to use a different port or are running the ML endpoint at a different location
you can change them with command-line options:

    python app.py --port=[new port] --ml-endpoint=[endpoint url including protocol and port]

### Instructions for Docker (Optional)

To run the web app with Docker the containers running the webserver and the REST endpoint need to share the same network stack. This is done in the following steps.

Modify the command that runs the Image Caption Generator REST endpoint to map an additional port in the container to a port on the host machine. In the example below it is mapped to port 8088 on the host but other ports can also be used.

    docker run -it -p 5000:5000 -p 8088:8088 --name max-im2txt max-im2txt

Build the web app image by running:

    docker build -t webapp .

Run the web app container using:

    docker run --net='container:max-im2txt' -it webapp

## Third-Party Sources

This web app includes the following third-party javascript and css libraries

- [Bootstrap 3](https://getbootstrap.com)
- [D3.js](https://d3js.org)
- [d3-cloud](https://github.com/jasondavies/d3-cloud)
- [Featherlight](https://noelboss.github.io/featherlight/)
- [Glyphicons](http://glyphicons.com)
- [Image Picker](http://rvera.github.io/image-picker/)
- [JQuery](https://jquery.com)

The default image set was curated from [Pexels](https://www.pexels.com)

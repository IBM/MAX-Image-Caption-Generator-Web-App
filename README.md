[![Build Status](https://travis-ci.org/IBM/MAX-Image-Caption-Generator-Web-App.svg?branch=master)](https://travis-ci.org/IBM/MAX-Image-Caption-Generator-Web-App)

# Create a web app to interact with machine learning generated image captions

Every day 2.5 quintillion bytes of data are created, based on an
[IBM study](https://public.dhe.ibm.com/common/ssi/ecm/wr/en/wrl12345usen/watson-customer-engagement-watson-marketing-wr-other-papers-and-reports-wrl12345usen-20170719.pdf).
A lot of that data is unstructured data, such as large texts, audio recordings, and images. In order to do something
useful with the data, we must first convert it to structured data.

In this Code Pattern we will use one of the models from the
[Model Asset Exchange (MAX)](https://developer.ibm.com/code/exchanges/models/),
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

![Architecture](doc/source/images/architecture.jpg)

## Flow

1. Server sends default images to Model API and receives caption data.
2. User interacts with Web UI containing default content and uploads image(s).
3. Web UI requests caption data for image(s) from Server and updates content when data is returned.
4. Server sends image(s) to Model API and receives caption data to return to Web UI.

## Included Components

* [IBM Model Asset Exchange](https://developer.ibm.com/code/exchanges/models/): A place for developers to find and use
free and open source deep learning models.
* [Docker](https://www.docker.com): Docker is a tool designed to make it easier to create, deploy, and run applications
by using containers.

## Featured Technologies

* [Python](https://www.python.org/): Python is a programming language that lets you work more quickly and integrate
your systems more effectively.
* [JQuery](https://jquery.com): jQuery is a cross-platform JavaScript library designed to simplify the client-side
scripting of HTML.
* [Bootstrap 3](https://getbootstrap.com): Bootstrap is a free and open-source front-end library for designing websites
and web applications.
* [Pexels](https://www.pexels.com): Pexels provides high quality and completely free stock photos licensed under the
Creative Commons Zero (CC0) license.

# Watch the Video

<!-- TODO: embed link to youtube video -->

# Steps
<!--
Use the ``Deploy to IBM Cloud`` button **OR** run locally.

## Deploy to IBM Cloud

[![Deploy to IBM Cloud](https://bluemix.net/deploy/button.png)](https://bluemix.net/deploy?repository=https://github.com/IBM/MAX-Image-Caption-Generator-Web-App)

1. Press the above ``Deploy to IBM Cloud`` button and then click on ``Deploy``. If you do not have an IBM Cloud account
yet, you will need to create one.

2. In Toolchains, click on ``Delivery Pipeline`` to watch while the app is deployed. Once deployed, the app can be
viewed by clicking ``View app``.

![Deploy to IBM Cloud](doc/source/images/ibm-cloud-deploy.png)

> Note: When deploying to IBM Cloud, by clicking the ``Deploy to IBM Cloud`` button above, a public Image Caption
Generator endpoint is provided and a new one is not created on your IBM Cloud account.

## Run Locally

> NOTE: These steps are only needed when running locally instead of using the ``Deploy to IBM Cloud`` button.
-->
#### Setting up the MAX Model

1. [Build the Model](#1-build-the-model)
2. [Deploy the Model](#2-deploy-the-model)
3. [Experimenting with the API (Optional)](#3-experimenting-with-the-api-optional)

#### Starting the Web App

1. [Installing dependencies](#1-installing-dependencies)
2. [Running the server](#2-running-the-server)
3. [Configuring ports (Optional)](#3-configuring-ports-optional)
4. [Instructions for Docker (Optional)](#4-instructions-for-docker-optional)

### Setting up the MAX Model

> NOTE: The set of instructions in this section are a modified version of the one found on the
[Image Caption Generator Project Page](https://github.com/IBM/MAX-Image-Caption-Generator)

#### 1. Build the Model

Clone the Image Caption Generator model locally. In a terminal, run the following command:

    git clone https://github.com/IBM/MAX-Image-Caption-Generator.git

Change directory into the repository base folder:

    cd MAX-Image-Caption-Generator

To build the docker image locally, run:

    docker build -t max-im2txt .

All required model assets will be downloaded during the build process.

_Note_ that currently this docker image is CPU only (we will add support for GPU images later).

#### 2. Deploy the Model

To run the docker image, which automatically starts the model serving API, run:

    docker run -it -p 5000:5000 max-im2txt

#### 3. Experimenting with the API (Optional)

The API server automatically generates an interactive Swagger documentation page.
Go to `http://localhost:5000` to load it. From there you can explore the API and also create test requests.

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

### Starting the Web App

#### 1. Check out the code

Clone the Image Caption Generator Web App repository locally by running the following command:

    git clone https://github.com/IBM/MAX-Image-Caption-Generator-Web-App.git

> Note: You may need to `cd ..` out of the MAX-Image-Caption-Generator directory first

Then change directory into the local repository

    cd MAX-Image-Caption-Generator-Web-App

#### 2. Installing dependencies

Before running this web app you must install its dependencies:

    pip install -r requirements.txt

#### 3. Running the server

You then start the web app by running:

    python app.py

Once it's finished processing the default images (< 1 minute) you can then access the web app at:
[`http://localhost:8088`](http://localhost:8088)

The Image Caption Generator endpoint must be available at `http://localhost:5000` for the web app to successfully start.

#### 4. Configuring ports (Optional)

If you want to use a different port or are running the ML endpoint at a different location
you can change them with command-line options:

    python app.py --port=[new port] --ml-endpoint=[endpoint url including protocol and port]

#### 5. Instructions for Docker (Optional)

To run the web app with Docker the containers running the webserver and the REST endpoint need to share the same
network stack. This is done in the following steps:

Modify the command that runs the Image Caption Generator REST endpoint to map an additional port in the container to a
port on the host machine. In the example below it is mapped to port `8088` on the host but other ports can also be used.

    docker run -it -p 5000:5000 -p 8088:8088 --name max-im2txt max-im2txt

Build the web app image by running:

    docker build -t webapp .

Run the web app container using:

    docker run --net='container:max-im2txt' -it webapp

# Sample Output

![Web UI Screenshot](doc/source/images/webui.png)

# Troubleshooting

There is a large amount of user uploaded images in a long running web app

> When running the web app at `http://localhost:8088` an admin page is available at
> [`http://localhost:8088/cleanup`](http://localhost:8088/cleanup) that allows the user to delete all user uploaded
> files from the server.
>
> [Note: This deletes **all** user uploaded images]

![Admin UI Screenshot](doc/source/images/cleanup.png)

# Links

* [Model Asset eXchange (MAX)](https://developer.ibm.com/code/exchanges/models/)
* [Center for Open-Source Data & AI Technologies (CODAIT)](https://developer.ibm.com/code/open/centers/codait/)
* [MAX Announcement Blog](https://developer.ibm.com/code/2018/03/20/igniting-a-community-around-deep-learning-models-with-model-asset-exchange-max/)

## Libraries used in this Code Pattern
* [D3.js](https://d3js.org): D3.js is a JavaScript library for manipulating documents based on data.
* [d3-cloud](https://github.com/jasondavies/d3-cloud): A Wordle-inspired word cloud layout written in JavaScript.
* [Featherlight](https://noelboss.github.io/featherlight/): Featherlight is a very lightweight jQuery lightbox plugin.
* [Glyphicons](http://glyphicons.com): GLYPHICONS is a library of precisely prepared monochromatic icons and symbols,
created with an emphasis to simplicity and easy orientation.
* [Image Picker](http://rvera.github.io/image-picker/): Image Picker is a simple jQuery plugin that transforms a select
element into a more user friendly graphical interface.

# Learn More

* **Artificial Intelligence Code Patterns**: Enjoyed this Code Pattern? Check out our other
[Artificial Intelligence Code Patterns](https://developer.ibm.com/code/technologies/artificial-intelligence/)
* **AI and Data Code Pattern Playlist**: Bookmark our
[playlist](https://www.youtube.com/playlist?list=PLzUbsvIyrNfknNewObx5N7uGZ5FKH0Fde) with all of our Code Pattern videos
* **Watson Studio**: Master the art of data science with IBM's [Watson Studio](https://dataplatform.ibm.com/)
* **Deep Learning with Watson Studio**: Design and deploy deep learning models using neural networks, easily scale to
hundreds of training runs. Learn more at [Deep Learning with Watson Studio](https://www.ibm.com/cloud/deep-learning).

# License
[Apache 2.0](LICENSE)

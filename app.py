#!/usr/bin/env python

#
# Copyright 2018 IBM Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import collections, json, logging, os, requests, signal, time, threading
from tornado import httpserver, ioloop, web
from tornado.options import define, options, parse_command_line

# Command Line Options
define("port", default=8088, help="Port the web app will run on")
define("ml-endpoint", default="http://localhost:5000", help="The Image Caption Generator REST endpoint")

# Setup Logging
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(levelname)s: %(message)s')

# Global variables
static_img_path = "static/img/images/"
temp_img_prefix = "MAX-"
image_captions = collections.OrderedDict()


class MainHandler(web.RequestHandler):
    def get(self):
        self.render("index.html", image_captions=image_captions)


class DetailHandler(web.RequestHandler):
    def get(self):
        image = self.get_argument('image', None)
        if not image:
            self.set_status(400)
            return self.finish("400: Missing image parameter")
        if image not in image_captions:
            self.set_status(404)
            return self.finish("404: Image not found")
        self.render("detail-snippet.html", image=image, predictions=image_captions[image])


class CleanupHandler(web.RequestHandler):
    def get(self):
        self.render("cleanup.html")

    def delete(self):
        clean_up()


class UploadHandler(web.RequestHandler):
    def post(self):
        finish_ret = []
        new_files = self.request.files['file']
        for file_des in new_files:
            file_name = temp_img_prefix + file_des['filename']
            rel_path = static_img_path + file_name
            output_file = open(rel_path, 'wb')
            output_file.write(file_des['body'])
            output_file.close()
            caption = run_ml(rel_path)
            finish_ret.append({"file_name": rel_path, "caption": caption[0]['caption']})
        sort_image_captions()
        self.finish(json.dumps(finish_ret))


# Runs ML on given image
def run_ml(img_path):
    img_file = {'image': open(img_path, 'rb')}
    r = requests.post(url=ml_endpoint, files=img_file)
    cap_json = r.json()
    caption = cap_json['predictions']
    image_captions[img_path] = caption
    return caption


def sort_image_captions():
    global image_captions
    image_captions = collections.OrderedDict(sorted(image_captions.items(), key=lambda t: t[0].lower()))
    logging.info(image_captions)


# Gets list of images with relative paths from static dir
def get_image_list():
    image_list = sorted(os.listdir(static_img_path))
    rel_img_list = [static_img_path + s for s in image_list]
    return rel_img_list


# Run all static images through ML
def prepare_metadata():
    threads = []

    rel_img_list = get_image_list()
    for img in rel_img_list:
        t = threading.Thread(target=run_ml, args=(img,))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    threads.clear()
    sort_image_captions()


# Deletes all files uploaded through the GUI and removes them from the dict
def clean_up():
    img_list = get_image_list()
    for img_file in img_list:
        if img_file.startswith(static_img_path + temp_img_prefix):
            os.remove(img_file)
            image_captions.pop(img_file)


def signal_handler(sig, frame):
    ioloop.IOLoop.current().add_callback_from_signal(shutdown)


def shutdown():
    logging.info("Cleaning up image files")
    clean_up()
    logging.info("Stopping web server")
    server.stop()
    ioloop.IOLoop.current().stop()


def make_app():
    handlers = [
        (r"/", MainHandler),
        (r"/upload", UploadHandler),
        (r"/cleanup", CleanupHandler),
        (r"/detail", DetailHandler)
    ]

    configs = {
        'static_path': 'static',
        'template_path': 'templates'
    }

    return web.Application(handlers, **configs)


def main():
    parse_command_line()

    global ml_endpoint
    ml_endpoint = options.ml_endpoint
    if '/model/predict' not in options.ml_endpoint:
        ml_endpoint = options.ml_endpoint + "/model/predict"

    logging.info("Connecting to ML endpoint at %s", ml_endpoint)

    try:
        resp = requests.get(ml_endpoint)
    except requests.exceptions.ConnectionError:
        logging.error("Cannot connect to the Image Caption Generator REST endpoint at %s", options.ml_endpoint)
        raise SystemExit

    logging.info("Starting web server")
    app = make_app()
    global server
    server = httpserver.HTTPServer(app)
    server.listen(options.port)
    signal.signal(signal.SIGINT, signal_handler)

    logging.info("Preparing ML metadata")
    start = time.time()
    prepare_metadata()
    end = time.time()
    logging.info("Metadata prepared in %s seconds", end - start)

    logging.info("Use Ctrl+C to stop web server")
    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()

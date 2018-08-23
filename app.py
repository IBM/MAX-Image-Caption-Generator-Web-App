#!/usr/bin/env python

#
# Copyright 2018 IBM Corp. All Rights Reserved.
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

import collections
import json
import logging
import mimetypes
import os
import requests
import signal
import time
import threading
import uuid
from tornado import httpserver, ioloop, web
from tornado.options import define, options, parse_command_line
try:
    import Queue as queue
except ImportError:
    import queue

# Command Line Options
define("port", default=8088, help="Port the web app will run on")
define("ml-endpoint", default="http://localhost:5000",
       help="The Image Caption Generator REST endpoint")

# Setup Logging
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"),
                    format='%(levelname)s: %(message)s')

# Global variables
static_img_path = "static/img/images/"
temp_img_prefix = "MAX-"
image_captions = collections.OrderedDict()
VALID_EXT = ['png', 'jpg', 'jpeg']
error_raised = []
app_cookie = 'max-image-caption-generator-web-app'


class BaseHandler(web.RequestHandler):
    def prepare(self):
        if not self.get_cookie(app_cookie):
            user_id = str(uuid.uuid4())
            self.set_cookie(app_cookie, user_id)
            logging.info('New web app cookie set: ' + user_id)
        else:
            logging.info('Previous web app cookie found: '
                         + self.get_cookie(app_cookie))


class MainHandler(BaseHandler):
    def get(self):
        self.render("index.html", image_captions=get_image_captions(self))


class DetailHandler(BaseHandler):
    def get(self):
        user_image_captions = get_image_captions(self)
        image = self.get_argument('image', None)
        if not image:
            self.set_status(400)
            return self.finish("400: Missing image parameter")
        if image not in user_image_captions:
            self.set_status(404)
            return self.finish("404: Image not found")
        self.render("detail-snippet.html", image=image,
                    predictions=user_image_captions[image])


class CleanupHandler(BaseHandler):
    def delete(self):
        clean_up(self)


class UploadHandler(BaseHandler):
    def post(self):
        try:
            requests.get(ml_endpoint)
        except requests.exceptions.ConnectionError:
            logging.error(
                "Lost connection to the model REST endpoint at " +
                options.ml_endpoint)
            self.send_error(404)
            return

        finish_ret = []
        threads = []
        ret_queue = queue.Queue()
        user_img_prefix = get_user_img_prefix(self)

        new_files = self.request.files['file']
        for file_des in new_files:
            file_name = user_img_prefix + file_des['filename']
            if valid_file_ext(file_name):
                rel_path = static_img_path + file_name
                with open(rel_path, 'wb') as output_file:
                    output_file.write(file_des['body'])
                t = threading.Thread(target=run_ml_queued,
                                     args=(rel_path, ret_queue))
                threads.append(t)
                t.start()

        for t in threads:
            t.join()

        sorted_ret = sorted(list(ret_queue.queue), key=lambda t: t[0].lower())
        for rel_path, caption in sorted_ret:
            finish_ret.append({
                "file_name": rel_path,
                "caption": caption[0]['caption']
            })

        if not finish_ret:
            self.send_error(400)
            return
        sort_image_captions()
        self.finish(json.dumps(finish_ret))


def get_user_img_prefix(self):
    cookie = self.get_cookie(app_cookie)
    user_id = cookie if cookie else ""
    return temp_img_prefix + user_id + "-"


def valid_user_img(self, img):
    default_img = not img.startswith(static_img_path + temp_img_prefix)
    user_img = img.startswith(static_img_path + get_user_img_prefix(self))
    current_user_img = user_img if self.get_cookie(app_cookie) else False
    return default_img or current_user_img


def get_image_captions(self):
    return collections.OrderedDict(
        (k, v) for k, v in image_captions.items() if valid_user_img(self, k)
    )


def run_ml_queued(img_path, ret_queue):
    caption = run_ml(img_path)
    ret_queue.put((img_path, caption))


def valid_file_ext(filename):
    return '.' in filename and filename.split('.', 1)[1].lower() in VALID_EXT


# Runs ML on given image
def run_ml(img_path):
    mime_type = mimetypes.guess_type(img_path)[0]
    with open(img_path, 'rb') as img_file:
        file_form = {'image': (img_path, img_file, mime_type)}
        r = requests.post(url=ml_endpoint, files=file_form)
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        error_raised.append(e)
        raise
    cap_json = r.json()
    caption = cap_json['predictions']
    image_captions[img_path] = caption
    return caption


def sort_image_captions():
    global image_captions
    image_captions = collections.OrderedDict(
        sorted(image_captions.items(), key=lambda t: t[0].lower()))


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
        t.start()

    for t in threads:
        t.join()

    sort_image_captions()


# Deletes all files uploaded through the GUI and removes them from the dict
def clean_up(self):
    img_prefix = get_user_img_prefix(self) if self else temp_img_prefix
    img_list = get_image_list()
    for img_file in img_list:
        if img_file.startswith(static_img_path + img_prefix):
            os.remove(img_file)
            image_captions.pop(img_file)


def signal_handler(sig, frame):
    ioloop.IOLoop.current().add_callback_from_signal(shutdown)


def shutdown():
    logging.info("Cleaning up image files")
    clean_up(None)
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
        ml_endpoint = options.ml_endpoint.rstrip('/') + "/model/predict"

    logging.info("Connecting to ML endpoint at %s", ml_endpoint)

    try:
        requests.get(ml_endpoint)
    except requests.exceptions.ConnectionError:
        logging.error(
            "Cannot connect to the Image Caption Generator REST endpoint at " +
            options.ml_endpoint)
        raise SystemExit

    logging.info("Starting web server")
    app = make_app()
    global server
    server = httpserver.HTTPServer(app)
    server.listen(options.port)
    signal.signal(signal.SIGINT, signal_handler)

    logging.info("Preparing ML metadata (this may take some time)")
    start = time.time()
    prepare_metadata()
    end = time.time()
    if error_raised:
        logging.info("Failed to prepare metadata, stopping web server")
        raise SystemExit
    logging.info("Metadata prepared in %s seconds", end - start)

    logging.info("Use Ctrl+C to stop web server")
    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()

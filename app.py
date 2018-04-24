import collections, json, logging, os, requests, signal, time
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
        self.finish(json.dumps(finish_ret))


# Runs ML on given image
def run_ml(img_path):
    img_file = {'image': open(img_path, 'rb')}
    r = requests.post(url=ml_endpoint, files=img_file)
    cap_json = r.json()
    caption = cap_json['predictions']
    image_captions[img_path] = caption
    return caption


# Gets list of images with relative paths from static dir
def get_image_list():
    image_list = sorted(os.listdir(static_img_path))
    rel_img_list = [static_img_path + s for s in image_list]
    return rel_img_list


# Run all static images through ML
def prepare_metadata():
    rel_img_list = get_image_list()
    for img in rel_img_list:
        run_ml(img)


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
        (r"/cleanup", CleanupHandler)
    ]

    configs = {
        'static_path': 'static',
        'template_path': 'templates'
    }

    return web.Application(handlers, **configs)


def main():
    parse_command_line()

    global ml_endpoint
    ml_endpoint = options.ml_endpoint + "/model/predict"
    logging.debug("Connecting to ML endpoint at %s", ml_endpoint)

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

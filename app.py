import logging, os, requests, signal, time
from tornado import httpserver, ioloop, web


# Setup Logging
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(levelname)s: %(message)s')

# Global variables
ml_endpoint = "http://localhost:5000/model/predict"
static_img_path = "static/img/"
temp_img_prefix = "MAX-"
image_captions = {}


class MainHandler(web.RequestHandler):
    def get(self):
        self.render("index.html", image_captions=image_captions)


class UploadHandler(web.RequestHandler):
    def post(self):
        file_des = self.request.files['file'][0]
        file_name = temp_img_prefix + file_des['filename']
        rel_path = static_img_path + file_name
        output_file = open(rel_path, 'wb')
        output_file.write(file_des['body'])
        output_file.close()
        caption = run_ml(rel_path)
        self.finish({"file_name": rel_path, "caption": caption})


# Runs ML on given image
def run_ml(img_path):
    img_file = {'image': open(img_path, 'rb')}
    r = requests.post(url=ml_endpoint, files=img_file)
    cap_json = r.json()
    caption = cap_json['predictions'][0]['caption']
    image_captions[img_path] = caption
    return caption


# Gets list of images with relative paths from static dir
def get_image_list():
    image_list = os.listdir(static_img_path)
    rel_img_list = [static_img_path + s for s in image_list]
    return rel_img_list


# Run all static images through ML
def prepare_metadata():
    rel_img_list = get_image_list()
    for img in rel_img_list:
        run_ml(img)


# Deletes all files uploaded through the GUI
def clean_up():
    img_list = get_image_list()
    for img_file in img_list:
        if img_file.startswith(static_img_path + temp_img_prefix):
            os.remove(img_file)


def signal_handler(sig, frame):
    ioloop.IOLoop.current().add_callback_from_signal(shutdown)


def shutdown():
    logging.info("Cleaning up image files")
    clean_up()
    logging.info("Stopping server")
    server.stop()
    ioloop.IOLoop.current().stop()


def make_app():
    handlers = [
        (r"/", MainHandler),
        (r"/upload", UploadHandler)
    ]

    configs = {
        'static_path': 'static',
        'template_path': 'templates'
    }

    return web.Application(handlers, **configs)


def main():
    try:
        resp = requests.get(ml_endpoint)
    except requests.exceptions.ConnectionError:
        logging.error("Cannot connect to the Object Detection API")
        logging.error("Please run the Object Detection API docker image first")
        raise SystemExit

    logging.info("Starting Server")
    global server
    app = make_app()
    server = httpserver.HTTPServer(app)
    server.listen(8088)
    signal.signal(signal.SIGINT, signal_handler)

    logging.info("Preparing ML Metadata")
    start = time.time()
    prepare_metadata()
    end = time.time()
    logging.info("Metadata prepared in %s seconds", end - start)

    logging.info("Use Ctrl+C to stop server")
    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()

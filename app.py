from os import listdir
import requests
import time
import tornado.ioloop as ioloop
import tornado.web as web


class MainHandler(web.RequestHandler):
    def get(self):
        self.render("index.html", image_captions=image_captions)


class UploadHandler(web.RequestHandler):
    def post(self):
        file_des = self.request.files['file'][0]
        file_name = "MAX-" + file_des['filename']
        rel_path = "static/img/" + file_name
        output_file = open(rel_path, 'wb')
        output_file.write(file_des['body'])
        output_file.close()
        caption = run_ml(rel_path)
        self.finish({"file_name": rel_path, "caption": caption})


image_captions = {}


def run_ml(img_path):
    ml_endpoint = "http://localhost:5000/model/predict"

    img_files = {'image': open(img_path, 'rb')}

    r = requests.post(url=ml_endpoint, files=img_files)

    cap_json = r.json()

    caption = cap_json['predictions'][0]['caption']

    image_captions[img_path] = caption

    return caption


def prepare_metadata():
    # Create list of images with relative paths
    rel_path = "static/img/"
    image_list = listdir(rel_path)
    rel_img_list = [rel_path + s for s in image_list]

    # Run images through ML
    for img in rel_img_list:
        run_ml(img)


def make_app():
    handlers = [
        (r"/", MainHandler),
        (r"/upload", UploadHandler)
    ]

    configs = {
        'static_path': 'static',
        'template_path': 'templates',
        'debug': True
    }

    web_app = web.Application(handlers, **configs)

    return web_app


def main():
    print("MAX WebApp: Setting up App")
    app = make_app()
    if not image_captions:
        print("MAX WebApp: Preparing ML Metadata")
        start = time.time()
        prepare_metadata()
        end = time.time()
        print("MAX WebApp: Metadata prepared in " + str(end - start) + " seconds")
    app.listen(8088)
    print("MAX WebApp: Ctrl+C to kill")
    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()

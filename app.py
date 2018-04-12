import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        file = self.request.files['file'][0]
        file_name = file['filename']
        output_file = open("static/img/MAX-" + file_name, 'wb')
        output_file.write(file['body'])
        self.finish("file " + file_name + " added")


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

    web_app = tornado.web.Application(handlers, **configs)

    return web_app


if __name__ == "__main__":
    app = make_app()
    app.listen(8088)
    tornado.ioloop.IOLoop.current().start()

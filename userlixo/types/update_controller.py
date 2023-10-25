class UpdateController:
    def __init__(self, cls):
        self.handlers = []
        self.cls = cls
        self.import_handlers()

    def import_handlers(self):
        for key in dir(self.cls):
            attribute = getattr(self.cls, key)
            if not callable(attribute):
                continue

            if hasattr(attribute, "register_handler"):
                self.handlers.append(attribute)

    def import_controller(self, controller: "UpdateController"):
        if not isinstance(controller, UpdateController):
            raise TypeError("controller must be a UpdateController")

        self.handlers.extend(controller.handlers)

    def register(self, client):
        for handler in self.handlers:
            handler.register_handler(client)

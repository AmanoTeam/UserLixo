from kink import inject

from userlixo.types import UpdateController


class Controller:
    def __init__(self, imports: list | None = None):
        if imports is None:
            imports = []

        self.imports = imports

    def __call__(self, cls) -> UpdateController:
        cls = inject(cls)
        controller = UpdateController(cls)

        for c in self.imports:
            controller.import_controller(c)

        cls.__controller__ = controller

        return cls

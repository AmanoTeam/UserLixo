def post_load(func):
    func.is_post_load = True
    return func

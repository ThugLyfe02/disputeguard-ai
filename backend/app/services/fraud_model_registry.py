models = {}


def register_model(name, model):

    models[name] = model

    return {"status": "registered", "model": name}


def get_model(name):

    return models.get(name)


def list_models():

    return list(models.keys())
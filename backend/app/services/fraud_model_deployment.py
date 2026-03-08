from app.services.fraud_model_registry import get_model


active_model = None


def deploy_model(name):

    global active_model

    model = get_model(name)

    if not model:
        return {"status": "model_not_found"}

    active_model = model

    return {"status": "deployed", "model": name}


def get_active_model():

    return active_model
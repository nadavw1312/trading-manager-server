def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        nonlocal instances
        print(instances, id(instances))
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
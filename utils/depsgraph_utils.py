def get_unique_name(object_instance):
    ob = get_object_data_from_instance(object_instance)
    prefix = ""

    if object_instance.is_instance:
        prefix = object_instance.parent.name + "_"
    
    return prefix + ob.name

def get_object_data_from_instance(object_instance):
    return object_instance.instance_object if object_instance.is_instance else object_instance.object
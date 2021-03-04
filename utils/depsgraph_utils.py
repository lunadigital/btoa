def get_unique_name(object_instance):
    prefix = ""
    name = ""

    if hasattr(object_instance, "is_instance"):
        if object_instance.is_instance:
            prefix = object_instance.parent.name + "_"
        
        ob = get_object_data_from_instance(object_instance)
        name = ob.name + "_MESH"
    else: # assume it's a material
        if object_instance.library:
            prefix = object_instance.library.name + "_"
        
        name = object_instance.name + "_MATERIAL"

    return prefix + name

def get_object_data_from_instance(object_instance):
    return object_instance.instance_object if object_instance.is_instance else object_instance.object
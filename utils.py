import traceback
import bpy

def register_quietly(clazz):
    try:
        bpy.utils.register_class(clazz)
    except:
        pass

def unregister_quietly(clazz):
    try:
        bpy.utils.unregister_class(clazz)
    except:
        traceback.print_exc()

import importlib

if "bind_metarig_to_rigify_rig" in locals():
    importlib.reload(bind_metarig_to_rigify_rig)
else:
    from . import bind_metarig_to_rigify_rig

if "bind_genesis8_with_rigify" in locals():
    importlib.reload(bind_genesis8_with_rigify)
else:
    from . import bind_genesis8_with_rigify

bl_info = {
    "name": "VSW Blender Tools",
    "category": "Rigging",
    "description": "Some of my custom tools",
    "location": "All over the places",
    "blender":(2,93,0)
}


def register():
    bind_metarig_to_rigify_rig.register()
    bind_genesis8_with_rigify.register()

def unregister():
    bind_metarig_to_rigify_rig.unregister()
    bind_genesis8_with_rigify.unregister()

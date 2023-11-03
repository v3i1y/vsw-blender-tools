import importlib

if "bind_metarig_to_rigify_rig" in locals():
    importlib.reload(bind_metarig_to_rigify_rig)
else:
    from . import bind_metarig_to_rigify_rig

if "bind_genesis8_with_rigify" in locals():
    importlib.reload(bind_genesis8_with_rigify)
else:
    from . import bind_genesis8_with_rigify


if "diffeomorphic_helper" in locals():
    importlib.reload(diffeomorphic_helper)
else:
    from . import diffeomorphic_helper


if "canvas_helper" in locals():
    importlib.reload(canvas_helper)
else:
    from . import canvas_helper

if "vertex_group_renderer" in locals():
    importlib.reload(vertex_group_renderer)
else:
    from . import vertex_group_renderer

if "hair_helper" in locals():
    importlib.reload(hair_helper)
else:
    from . import hair_helper

if "hair_thickness_adjust" in locals():
    importlib.reload(hair_thickness_adjust)
else:
    from . import hair_thickness_adjust

if "vr_cursor" in locals():
    importlib.reload(vr_cursor)
else:
    from . import vr_cursor

bl_info = {
    "name": "VSW Blender Tools",
    "category": "Rigging",
    "description": "Some of my custom tools",
    "location": "All over the places",
    "blender":(2,93,0)
}


def register():
    diffeomorphic_helper.register()
    bind_metarig_to_rigify_rig.register()
    bind_genesis8_with_rigify.register()
    canvas_helper.register()
    vertex_group_renderer.register()
    hair_helper.register()
    hair_thickness_adjust.register()
    vr_cursor.register()

def unregister():
    diffeomorphic_helper.unregister()
    bind_metarig_to_rigify_rig.unregister()
    bind_genesis8_with_rigify.unregister()
    canvas_helper.unregister()
    vertex_group_renderer.unregister()
    hair_helper.unregister()
    hair_thickness_adjust.unregister()
    vr_cursor.unregister()

def menu_func(self, context):
    hair_helper.menu_func(self, context)
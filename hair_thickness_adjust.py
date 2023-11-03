import bpy

class AdjustThicknessOperator(bpy.types.Operator):
    bl_idname = "object.adjust_thickness"
    bl_label = "Adjust Thickness Weight"
    
    initial_wegits = {}
    
    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            # Calculate difference and clamp the value
            diff = (event.mouse_x - self.init_mouse_x) * 0.002

            vg = context.object.vertex_groups.get("thickness")
            if vg:
                bpy.ops.object.mode_set(mode='OBJECT')  # Temporarily set to object mode to set weights
                for v in [v for v in context.object.data.vertices if v.select]:
                    value = min(max(self.initial_wegits[v.index] + diff, 0.0), 1.0)
                    vg.add([v.index], value, 'REPLACE')
                bpy.ops.object.mode_set(mode='EDIT')  # Set back to edit mode

            return {'RUNNING_MODAL'}
        
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}
        
        elif event.type == 'LEFTMOUSE':
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object and context.mode == 'EDIT_MESH':
            self.init_mouse_x = event.mouse_x
            # We use 0.5 as a starting default. You can modify this to grab the actual weight if needed.

            # compute the initial value
            self.initial_wegits = {}
            bpy.ops.object.mode_set(mode='OBJECT')  # Temporarily set to object mode to get weights
            for v in [v for v in context.object.data.vertices if v.select]:
                try:
                    self.initial_wegits[v.index] = context.object.vertex_groups.get("thickness").weight(v.index)
                except RuntimeError:
                    self.initial_wegits[v.index] = 0.0
            bpy.ops.object.mode_set(mode='EDIT')  # Set back to edit mode

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "You must be in Edit Mode!")
            return {'CANCELLED'}

# Store keymaps here to access after registration
addon_keymaps = []

def register():
    bpy.utils.register_class(AdjustThicknessOperator)
    
    # Handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')
    kmi = km.keymap_items.new(AdjustThicknessOperator.bl_idname, 'D', 'PRESS', ctrl=False, shift=False)
    addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_class(AdjustThicknessOperator)
    
    # Unregister the keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

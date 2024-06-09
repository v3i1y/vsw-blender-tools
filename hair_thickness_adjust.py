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

class RotateAroundX(bpy.types.Operator):
    """Rotate around X Axis interactively"""
    bl_idname = "mesh.rotate_around_x_interactive"
    bl_label = "Rotate Around X Axis Interactive"

    def execute(self, context):
        # Call the rotate operator in interactive mode
        bpy.ops.transform.rotate('INVOKE_DEFAULT', orient_axis='X', orient_type='NORMAL')
        return {'FINISHED'}

# Store keymaps here to access after registration
addon_keymaps = []

def apply_all_modifiers(context):
    bpy.ops.object.mode_set(mode='OBJECT')  # Ensure we are in object mode
    for obj in context.selected_objects:
        if obj.type == 'MESH':
            for modifier in obj.modifiers:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bpy.ops.object.mode_set(mode='EDIT')  # Switch to edit mode to recalculate normals
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set(mode='OBJECT')  # Back to object mode
            bpy.ops.object.modifier_add(type='SUBSURF')  # Add subdivision surface modifier

class ApplyModifiersAndRecalcNormals(bpy.types.Operator):
    """Apply all modifiers in order, apply transform and rotation, recalculate normals outside, add a subdivision surface modifier"""
    bl_idname = "object.apply_modifiers_and_recalc_normals"
    bl_label = "Apply Modifiers and Recalc Normals"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.mode == 'OBJECT'

    def execute(self, context):
        apply_all_modifiers(context)
        return {'FINISHED'}

def mask_by_edit_mode_selection(context):
    bpy.ops.mesh.select_all(action='INVERT')  # Invert selection
    bpy.ops.mesh.hide(unselected=False)  # Hide selected
    bpy.ops.object.mode_set(mode='SCULPT')  # Switch to sculpt mode

    bpy.data.scenes['Scene'].tool_settings.sculpt.show_mask = False
    
    bpy.ops.paint.mask_flood_fill(mode='INVERT')  # Correctly invert mask in Sculpt Mode
    bpy.ops.object.mode_set(mode='EDIT')  # Temporarily switch back to Edit Mode to reveal all
    bpy.ops.mesh.reveal()  # Correctly reveal all hidden mesh
    bpy.ops.object.mode_set(mode='SCULPT')  # Switch back to Sculpt Mode

    bpy.data.scenes['Scene'].tool_settings.sculpt.show_mask = True
    bpy.ops.paint.mask_flood_fill(mode='INVERT')  # Correctly invert mask in Sculpt Mode

class MaskByEditModeSelection(bpy.types.Operator):
    """Invert selection in Edit Mode, hide selected, switch to Sculpt Mode, invert mask, and unhide mesh"""
    bl_idname = "object.mask_by_edit_mode_selection"
    bl_label = "Mask by Edit Mode Selection"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        mask_by_edit_mode_selection(context)
        return {'FINISHED'}

class ToggleSculptMaskOperator(bpy.types.Operator):
    """Toggle Sculpt Mask Visibility"""
    bl_idname = "sculpt.toggle_sculpt_mask"
    bl_label = "Toggle Sculpt Mask"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.tool_settings.sculpt.show_mask = not context.scene.tool_settings.sculpt.show_mask
        return {'FINISHED'}

class SculptHairHelperPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Sculpt Hair Helper"
    bl_idname = "OBJECT_PT_sculpthairhelper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    # bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        
        # one button for converting curve to mesh
        opt = layout.operator(
            "object.convert",
            text="Convert to Mesh",    
        )
        opt.target = 'MESH'
        layout.operator("object.apply_modifiers_and_recalc_normals", text="Apply Modifiers")
        layout.operator("object.mask_by_edit_mode_selection", text="Mask by Edit Mode Selection")
        layout.operator("sculpt.toggle_sculpt_mask", text="Toggle Sculpt Mask Visibility")

    # @classmethod
    # def poll(cls, context):
    #     return context.mode in {'OBJECT', 'EDIT_MESH'}


def register():
    bpy.utils.register_class(AdjustThicknessOperator)
    bpy.utils.register_class(RotateAroundX)
    bpy.utils.register_class(ApplyModifiersAndRecalcNormals)
    bpy.utils.register_class(SculptHairHelperPanel)
    bpy.utils.register_class(MaskByEditModeSelection)
    bpy.utils.register_class(ToggleSculptMaskOperator)
    
    # Handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')
    kmi = km.keymap_items.new(AdjustThicknessOperator.bl_idname, 'D', 'PRESS', ctrl=False, shift=False)
    addon_keymaps.append((km, kmi))

    # km = wm.keyconfigs.addon.keymaps.new(name='Mesh', space_type='EMPTY')
    kmi = km.keymap_items.new(RotateAroundX.bl_idname, 'D', 'PRESS', ctrl=True, shift=False)
    addon_keymaps.append((km, kmi))


def unregister():
    bpy.utils.unregister_class(AdjustThicknessOperator)
    bpy.utils.unregister_class(RotateAroundX)
    bpy.utils.unregister_class(ApplyModifiersAndRecalcNormals)
    bpy.utils.unregister_class(SculptHairHelperPanel)
    bpy.utils.unregister_class(MaskByEditModeSelection)
    bpy.utils.unregister_class(ToggleSculptMaskOperator)

    # Unregister the keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
import bpy
from bpy.types import Operator, Panel
from bpy_extras import view3d_utils

class VRMCT_OT_EnableCursorTracking(bpy.types.Operator):
    bl_idname = "vrmct.enable_cursor_tracking"
    bl_label = "Enable Cursor Tracking"

    _timer = None

    def modal(self, context, event):
        if event.type == 'TIMER':  # Update on every timer tick
            self.update_cursor_tracker_position(context, event)
        
        if not context.scene.vrmct_is_enabled:  # If tracking is disabled, stop the modal
            self.cancel(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        context.scene.vrmct_is_enabled = True  # A property we'll set up later to track if our system is enabled
        self._timer = context.window_manager.event_timer_add(0.01, window=context.window)  # Add a timer for frequent updates
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)

    def update_cursor_tracker_position(self, context, event):
        """Actual logic to update the 'cursor_tracker' object's position"""
        if "cursor_tracker" not in bpy.data.objects:
            print("cursor_tracker object not found!")
            return
        
        tracker = bpy.data.objects["cursor_tracker"]

        # Convert mouse 2D coordinates to 3D space.
        region = context.region
        rv3d = context.region_data
        coord = (event.mouse_region_x, event.mouse_region_y)
        
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        # This will set the location of the cursor_tracker to where your mouse is pointing in the 3D viewport.
        # You can adjust this logic to better suit your needs.
        tracker.location = ray_origin + view_vector

class VRMCT_OT_DisableCursorTracking(Operator):
    bl_idname = "vrmct.disable_cursor_tracking"
    bl_label = "Disable Cursor Tracking"

    def execute(self, context):
        context.scene.vrmct_is_enabled = False
        return {'FINISHED'}

class VRMCT_PT_CursorTrackingPanel(Panel):
    bl_label = "VR Mouse Cursor Tracker"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'VR'

    def draw(self, context):
        layout = self.layout
        
        # Add buttons to panel
        layout.operator("vrmct.enable_cursor_tracking")
        layout.operator("vrmct.disable_cursor_tracking")

classes = (
    VRMCT_OT_EnableCursorTracking,
    VRMCT_OT_DisableCursorTracking,
    VRMCT_PT_CursorTrackingPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.vrmct_is_enabled = bpy.props.BoolProperty(default=False, description="Is VR Mouse Cursor Tracking enabled?")
    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.vrmct_is_enabled

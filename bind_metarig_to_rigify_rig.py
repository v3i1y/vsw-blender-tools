import bpy
import re
from bpy.props import PointerProperty
from . import utils

class RigifyRigBinder_PT_Panel(bpy.types.Panel):
    bl_label = "Metarig to Rigify Rig Binder"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(self, context):
        return bpy.context.object.type == 'ARMATURE' and bpy.context.object.pose.bones.get('spine') != None and bpy.context.object.pose.bones.get('spine.001') != None
    
    def draw(self, context):
        self.layout.prop(context.object.data, "binding_target_rig", text="Target Rig")
        self.layout.operator("vsw.rigifybind")
        self.layout.operator("vsw.rigifyunbind")   

class ArmatureBindToRigifyRig(bpy.types.Operator):
    bl_idname = "vsw.rigifybind"
    bl_label = "Bind"
    
    def execute(self, context):
        current_rig = bpy.context.object
        target_rig = current_rig.data.binding_target_rig
        bpy.ops.object.mode_set(mode='OBJECT')
        for bone in current_rig.pose.bones:
            copyLocConstraints = [ c for c in bone.constraints if c.name == 'BIND_TO_RIGIFY_RIG' ]
            for c in copyLocConstraints:
                bone.constraints.remove( c ) # Remove constraint
            
            if bone.bone.use_deform:
                crc = bone.constraints.new('COPY_TRANSFORMS')
                crc.target = target_rig
                crc.name = 'BIND_TO_RIGIFY_RIG'
                crc.subtarget = 'DEF-' + bone.name
        return{'FINISHED'}

class ArmatureUnbindToRigifyRig(bpy.types.Operator):
    bl_idname = "vsw.rigifyunbind"
    bl_label = "Unbind"
    
    def execute(self, context):
        current_rig = bpy.context.object
        bpy.ops.object.mode_set(mode='OBJECT')
        for bone in current_rig.pose.bones:
            copyLocConstraints = [ c for c in bone.constraints if c.name == 'BIND_TO_RIGIFY_RIG' ]
            for c in copyLocConstraints:
                bone.constraints.remove( c ) # Remove constraint
        return{'FINISHED'}

def register():
    # tools to link metarig to rigifyrig
    utils.register_quietly(RigifyRigBinder_PT_Panel)
    utils.register_quietly(ArmatureBindToRigifyRig)
    utils.register_quietly(ArmatureUnbindToRigifyRig)

    bpy.types.Armature.binding_target_rig = PointerProperty(type=bpy.types.Object,
        name="Binding Target Rig",
        description="Binding target rig",
        poll=lambda self, obj: obj.type == 'ARMATURE' and obj.data is not self)
    
def unregister():
    utils.unregister_quietly(RigifyRigBinder_PT_Panel)
    utils.unregister_quietly(ArmatureBindToRigifyRig)
    utils.unregister_quietly(ArmatureUnbindToRigifyRig)



from . import utils
from bpy.props import *
from bpy.types import (Panel,Menu,Operator,PropertyGroup,AddonPreferences)
from pathlib import Path
import bpy
import json
import os
import random

def pose_file_path():
    path = "~/daz_pos_files.json"
    filepath = os.path.expanduser(path).replace("\\", "/")
    return filepath.rstrip("/ ")


class DiffHelperPreferences(AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        layout.label(text="Diffeomorphic Helper Preferences")
        layout.prop(self, "pose_files_path")

class DiffHelperRandomPose(Operator):
    bl_idname = "vsw.random_pose"
    bl_label = "Diff Helper"
    bl_description = "Diff Helper"
    bl_options = { "REGISTER", "UNDO" }

    def execute(self, context):

        with open(pose_file_path()) as f:
            files = json.load(f)
            index = random.randint(0, len(files) - 1)
            print(files[index])

            bpy.ops.daz.import_pose(daz_pose_file=files[index])
        return{'FINISHED'}
class DiffHelperResetRigifyControls(Operator):
    bl_idname = "vsw.reset_rigify_controls"
    bl_label = "Diff Helper"
    bl_description = "Diff Helper"
    bl_options = { "REGISTER", "UNDO" }

    def execute(self, context):
        rigid = context.active_object.data['rig_id']
        def fk2ik():
                getattr(bpy.ops.pose, "rigify_limb_ik2fk_" + rigid)(
                'INVOKE_DEFAULT',
                prop_bone=prop_bone,
                fk_bones=fk_bones,
                ik_bones=ik_bones,
                ctrl_bones=ctrl_bones,
                extra_ctrls=extra_ctrls)
        
        # footR
        prop_bone = 'thigh_parent.R'
        fk_bones = '["thigh_fk.R", "shin_fk.R", "foot_fk.R"]'
        ik_bones = '["thigh_ik.R", "MCH-shin_ik.R", "MCH-thigh_ik_target.R"]'
        ctrl_bones = '["thigh_ik.R", "thigh_ik_target.R", "foot_ik.R"]'
        extra_ctrls = '["foot_heel_ik.R", "foot_spin_ik.R"]'
        fk2ik()

        # footL
        prop_bone = 'thigh_parent.L'
        fk_bones = '["thigh_fk.L", "shin_fk.L", "foot_fk.L"]'
        ik_bones = '["thigh_ik.L", "MCH-shin_ik.L", "MCH-thigh_ik_target.L"]'
        ctrl_bones = '["thigh_ik.L", "thigh_ik_target.L", "foot_ik.L"]'
        extra_ctrls = '["foot_heel_ik.L", "foot_spin_ik.L"]'
        fk2ik()
        
        # handR
        prop_bone = 'upper_arm_parent.R'
        fk_bones = '["upper_arm_fk.R", "forearm_fk.R", "hand_fk.R"]'
        ik_bones = '["upper_arm_ik.R", "MCH-forearm_ik.R", "MCH-upper_arm_ik_target.R"]'
        ctrl_bones = '["upper_arm_ik.R", "upper_arm_ik_target.R", "hand_ik.R"]'
        extra_ctrls = '[]'
        fk2ik()

        # handL
        prop_bone = 'upper_arm_parent.L'
        fk_bones = '["upper_arm_fk.L", "forearm_fk.L", "hand_fk.L"]'
        ik_bones = '["upper_arm_ik.L", "MCH-forearm_ik.L", "MCH-upper_arm_ik_target.L"]'
        ctrl_bones = '["upper_arm_ik.L", "upper_arm_ik_target.L", "hand_ik.L"]'
        extra_ctrls = '[]'
        fk2ik()

        pose_bones = context.active_object.pose.bones
        pose_bones['upper_arm_parent.L']['IK_FK'] = 0
        pose_bones['upper_arm_parent.R']['IK_FK'] = 0
        pose_bones['thigh_parent.L']['IK_FK'] = 0
        pose_bones['thigh_parent.R']['IK_FK'] = 0

        view_layers = context.active_object.data.layers
        view_layers[0] = True
        for i in range(1, len(view_layers) - 1):
            view_layers[i] = False

        view_layers[3] = True
        view_layers[4] = True
        view_layers[5] = True
        view_layers[6] = True
        view_layers[7] = True
        view_layers[10] = True
        view_layers[13] = True
        view_layers[16] = True
        view_layers[19] = True

        return{'FINISHED'}

class DiffHelperSetRandomPosePath(Operator):
    bl_idname = "vsw.random_pose_path"
    bl_label = "Diff Helper"
    bl_description = "Diff Helper"
    bl_options = { "REGISTER", "UNDO" }

    directory: StringProperty(subtype="DIR_PATH")

    def invoke(self, context, event):
        print("invoked!")
        context.window_manager.fileselect_add(self)

        return{'FINISHED'}

    def execute(self, context):
        pose_files = list(Path(self.directory).rglob("*.duf"))
        pose_files = [ str(x) for x in pose_files ]
        with open(pose_file_path(), 'w+') as f:
            f.write(json.dumps(pose_files))
        return{'FINISHED'}

class DiffHelperPanel_PT_PANEL(Panel):
    bl_idname = "DiffHelper_PT_SidePanel"
    bl_label = "Diff Helper"
    bl_category = "Item"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return True

    pose_files_path: StringProperty(
        name="Pose Files Path",
        subtype="DIR_PATH"
    )

    def draw(self, context):
        layout = self.layout

        col = layout.column()

        box = col.box()
        row = box.row()
        row.operator("vsw.random_pose_path", icon = "FILE_FOLDER", text = "Select Pose Directory")
        row = box.row()
        row.operator("vsw.reset_rigify_controls", icon = "FILE_REFRESH", text = "Reset Rigify Controls")

        box = col.box()
        row = box.row()
        row.operator("vsw.random_pose", icon = "ARMATURE_DATA", text = "Load Random Pose")


def register():
    utils.register_quietly(DiffHelperPreferences)
    utils.register_quietly(DiffHelperRandomPose)
    utils.register_quietly(DiffHelperSetRandomPosePath)
    utils.register_quietly(DiffHelperResetRigifyControls)
    utils.register_quietly(DiffHelperPanel_PT_PANEL)

def unregister():
    utils.unregister_quietly(DiffHelperPreferences)
    utils.unregister_quietly(DiffHelperRandomPose)
    utils.unregister_quietly(DiffHelperSetRandomPosePath)
    utils.unregister_quietly(DiffHelperResetRigifyControls)
    utils.unregister_quietly(DiffHelperPanel_PT_PANEL)

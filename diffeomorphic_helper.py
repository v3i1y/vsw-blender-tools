
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

    fingers: BoolProperty()

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
        pose_bones = context.active_object.pose.bones

        if not self.fingers:
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

            pose_bones['upper_arm_parent.L']['IK_FK'] = 0
            pose_bones['upper_arm_parent.R']['IK_FK'] = 0
            pose_bones['thigh_parent.L']['IK_FK'] = 0
            pose_bones['thigh_parent.R']['IK_FK'] = 0
        else:
            for lr in ('R', 'L'):
                for finger in ('thumb', 'f_index', 'f_middle', 'f_ring', 'f_pinky'):
                    output_bones = '["' + finger + '.01_ik.' + lr + '"]'
                    input_bones = '["' +finger + '.01.' + lr + '.001"]'
                    ctrl_bones = '["' + finger + '.01_master.' + lr + '", "' + finger + '.01.' + lr + '", "' + finger + '.02.' + lr + '", "' + finger + '.03.' + lr + '", "' + finger + '.01.' + lr + '.001"]'
                    locks = (False, True, True)
                    tooltip = 'IK to FK'
                    print(ctrl_bones)

                    getattr(bpy.ops.pose, "rigify_generic_snap_" + rigid)(
                        'INVOKE_DEFAULT',
                        output_bones=output_bones,
                        input_bones=input_bones,
                        ctrl_bones=ctrl_bones,
                        locks=locks,
                        tooltip=tooltip)
                    pose_bones[finger + '.01_ik.' + lr]['FK_IK'] = 1

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

class DiffHelperSoloLayers(Operator):
    bl_idname = "vsw.solo_pose_layers"
    bl_label = "Diff Helper"
    bl_description = "Diff Helper"
    bl_options = { "REGISTER", "UNDO" }
    layer_indices: StringProperty()
    def execute(self, context):
        indices_str = self.layer_indices.split(',')
        indices = set([ int(s) for s in indices_str if s])
        view_layers = context.active_object.data.layers
        for i in range(0, 31):
            view_layers[i] = i in indices
        return{'FINISHED'}

class DiffHelperResetPose(Operator):
    bl_idname = "vsw.reset_pose"
    bl_label = "Diff Helper"
    bl_description = "Diff Helper"
    bl_options = { "REGISTER", "UNDO" }
    layer_indices: StringProperty()
    def execute(self, context):
        bones = context.active_object.pose.bones

        for bone in bones:
            layer = 0
            for i in range(0, 31):
                if context.active_object.data.bones[bone.name].layers[i]:
                    layer = i
                    break
            
            if layer < 31 - 4:
                bone.location = (0, 0, 0)
                bone.rotation_euler = (0, 0, 0)
                bone.scale = (1, 1, 1)

        bones['upper_arm_parent.L']['IK_FK'] = 0
        bones['upper_arm_parent.R']['IK_FK'] = 0
        bones['thigh_parent.L']['IK_FK'] = 0
        bones['thigh_parent.R']['IK_FK'] = 0
        for lr in ('R', 'L'):
            for finger in ('thumb', 'f_index', 'f_middle', 'f_ring', 'f_pinky'):
                bones[finger + '.01_ik.' + lr]['FK_IK'] = 0
        return{'FINISHED'}

class DiffHelperToggleShading(Operator):
    bl_idname = "vsw.toggle_shading"
    bl_label = "Diff Helper"
    bl_description = "Diff Helper"
    bl_options = { "REGISTER", "UNDO" }
    layer_indices: StringProperty()
    def execute(self, context):
        amat = context.active_object
        meshes = [ c for c in amat.children if c.type == 'MESH']
        for mesh in meshes:
            materials = mesh.data.materials
            for i in range(len(materials)):
                m = materials[i]
                if m.name.endswith('.Flat'):
                    materials[i] = bpy.data.materials[m.name.replace('.Flat', '.Shaded')]
                if m.name.endswith('.Shaded'):
                    materials[i] = bpy.data.materials[m.name.replace('.Shaded', '.Flat')]

        return{'FINISHED'}

class DiffHelperPanel_PT_PANEL(Panel):
    bl_idname = "DiffHelper_PT_SidePanel"
    bl_label = "Diff Helper"
    bl_category = "Item"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(self, context):
        try:
            return not not context.active_object.data.get("rig_id")
        except (AttributeError, KeyError, TypeError):
            return False

    pose_files_path: StringProperty(
        name="Pose Files Path",
        subtype="DIR_PATH"
    )

    def draw(self, context):
        layout = self.layout

        col = layout.column()

        col.label(text="Settings")
        box = col.box()
        row = box.row()
        row.operator("vsw.random_pose_path", icon = "FILE_FOLDER", text = "Select Pose Directory")

        col.label(text="Toggle View Layers")
        box = col.box()
        row = box.row()
        props = row.operator("vsw.solo_pose_layers", text="Hide All")
        props.layer_indices = '0'
        row = box.row()
        props = row.operator("vsw.solo_pose_layers", text="Show All")
        props.layer_indices = '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19'
        row = box.row()
        props = row.operator("vsw.solo_pose_layers", text="Primay with Fingers")
        props.layer_indices = '3,4,7,10,13,16,5,6,19'
        row = box.row()
        props = row.operator("vsw.solo_pose_layers", text="Primary Bones")
        props.layer_indices = '3,4,7,10,13,16'
        row = box.row()
        props = row.operator("vsw.solo_pose_layers", text="Tweek Bones")
        props.layer_indices = '4,5,9,12,15,18'
        row = box.row()
        props = row.operator("vsw.solo_pose_layers", text="Fingers")
        props.layer_indices = '5'
        row = box.row()
        props = row.operator("vsw.solo_pose_layers", text="Fingers Details")
        props.layer_indices = '6,19'

        col.label(text="Shading")
        box = col.box()
        row = box.row()
        row.operator("vsw.toggle_shading", icon = "SHADING_RENDERED", text = "Toggle Shading")

        col.label(text="Load Pose")
        box = col.box()
        row = box.row()
        props = row.operator("vsw.reset_rigify_controls", icon = "SNAP_ON", text = "Arms IK to FK")
        props.fingers = False
        row = box.row()
        props = row.operator("vsw.reset_rigify_controls", icon = "SNAP_ON", text = "Fingers IK to FK")
        props.fingers = True
        row = box.row()
        row.operator("vsw.random_pose", icon = "ARMATURE_DATA", text = "Load Random Pose")
        row = box.row()
        row.operator("vsw.reset_pose", icon = "FILE_REFRESH", text = "Reset Pose")


def register():
    utils.register_quietly(DiffHelperPreferences)
    utils.register_quietly(DiffHelperRandomPose)
    utils.register_quietly(DiffHelperSetRandomPosePath)
    utils.register_quietly(DiffHelperResetRigifyControls)
    utils.register_quietly(DiffHelperPanel_PT_PANEL)
    utils.register_quietly(DiffHelperSoloLayers)
    utils.register_quietly(DiffHelperResetPose)
    utils.register_quietly(DiffHelperToggleShading)

def unregister():
    utils.unregister_quietly(DiffHelperPreferences)
    utils.unregister_quietly(DiffHelperRandomPose)
    utils.unregister_quietly(DiffHelperSetRandomPosePath)
    utils.unregister_quietly(DiffHelperResetRigifyControls)
    utils.unregister_quietly(DiffHelperPanel_PT_PANEL)
    utils.unregister_quietly(DiffHelperSoloLayers)
    utils.unregister_quietly(DiffHelperResetPose)
    utils.unregister_quietly(DiffHelperToggleShading)

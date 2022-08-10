import bpy
import re
from bpy.props import PointerProperty, BoolProperty
from . import utils
from mathutils import *

class DazRigifyBoneMapper:
    """
    format: [(daz_bone, metarig_bone, rigify_bone)]
    """
    bone_map = []
    
    """
    format: [(key_world, daz_merge_to_bone, symmetrize)]
    """
    daz_vertex_group_merge_map = [
        ('Toe', 'Toe', True),
        ('Metatarsals', 'Foot', True),
        
        ('Anus', 'pelvis', False),
        ('Genitals', 'pelvis', False),
        
        ('Teeth', 'head', False),
        ('Jaw', 'head', False),
        ('Toe', 'head', False),
        ('tongue', 'head', False),
        ('Lip', 'head', False),
        ('Eye', 'head', False),
        ('Chin', 'head', False),
        ('Cheek', 'head', False),
        ('Brow', 'head', False),
        ('Nasolabial', 'head', False),
        ('Nose', 'head', False),
        ('Nostril', 'head', False),
        ('Nasol', 'head', False),
        ('Ear', 'head', False),
        ('Squint', 'head', False)
    ]

    """
    format: [(key_world, daz_merge_to_bone, symmetrize)]
    """
    daz_vertex_group_merge_less_bone_map = [
        ('chestUpper', 'chestLower', False),
        ('neckUpper', 'neckLower', False)
    ]

    def __init__(self):
        # roots
        self.add_mapping('root', 'None', 'root')
        self.add_mapping('hip', 'None', 'torso')

        # spine
        self.add_mapping('pelvis', 'spine')
        self.add_mapping('abdomenLower', 'spine.001')
        self.add_mapping('abdomenUpper', 'spine.002')
        self.add_mapping('chestLower', 'spine.003')
        self.add_mapping('chestUpper', 'spine.006') # new bone

        # head
        self.add_mapping('neckLower', 'spine.004')
        self.add_mapping('neckUpper', 'spine.007') # new bone
        self.add_mapping('head', 'spine.005')

        # arms
        self.add_sym_mapping('Pectoral', 'breast')
        self.add_sym_mapping('Collar', 'shoulder')
        self.add_sym_mapping('ShldrBend', 'upper_arm')
        self.add_mapping('rShldrTwist', 'None', 'DEF-upper_arm.R.001')
        self.add_mapping('lShldrTwist', 'None', 'DEF-upper_arm.L.001')
        self.add_sym_mapping('ForearmBend', 'forearm')
        self.add_mapping('rForearmTwist', 'None', 'DEF-forearm.R.001')
        self.add_mapping('lForearmTwist', 'None', 'DEF-forearm.L.001')
        self.add_sym_mapping('Hand', 'hand')

        # hands
        self.add_sym_mapping('Carpal1', 'palm.01')
        self.add_sym_mapping('Carpal2', 'palm.02')
        self.add_sym_mapping('Carpal3', 'palm.03')
        self.add_sym_mapping('Carpal4', 'palm.04')
        self.add_finger_mapping('Thumb', 'thumb')
        self.add_finger_mapping('Index', 'f_index')
        self.add_finger_mapping('Mid', 'f_middle')
        self.add_finger_mapping('Ring', 'f_ring')
        self.add_finger_mapping('Pinky', 'f_pinky')

        # legs
        self.add_sym_mapping('ThighBend', 'thigh')
        self.add_mapping('rThighTwist', 'None', 'DEF-thigh.R.001')
        self.add_mapping('lThighTwist', 'None', 'DEF-thigh.L.001')
        self.add_sym_mapping('Shin', 'shin')
        self.add_sym_mapping('Foot', 'foot')
        self.add_sym_mapping('Toe', 'toe')

    def add_sym_mapping(self, dazBoneName, metarigBoneName, rigifyBoneName='GUESS'):
        self.add_mapping('r' + dazBoneName, metarigBoneName + ".R", rigifyBoneName + ".R")
        self.add_mapping('l' + dazBoneName, metarigBoneName + ".L", rigifyBoneName + ".L")

    def add_finger_mapping(self, dazBoneName, metarigBoneName, rigifyBoneName='GUESS'):
        self.add_sym_mapping(dazBoneName + "1", metarigBoneName + ".01", rigifyBoneName + ".01")
        self.add_sym_mapping(dazBoneName + "2", metarigBoneName + ".02", rigifyBoneName + ".02")
        self.add_sym_mapping(dazBoneName + "3", metarigBoneName + ".03", rigifyBoneName + ".03")

    def add_mapping(self, dazBoneName, metarigBoneName, rigifyBoneName='GUESS'):
        if 'GUESS' in rigifyBoneName:
            rigifyBoneName = 'DEF-' + metarigBoneName
        if 'None' in metarigBoneName:
            metarigBoneName = None
        if 'None' in rigifyBoneName:
            rigifyBoneName = None
        self.bone_map.append((dazBoneName, metarigBoneName, rigifyBoneName))
    
    def get_mappings(self):
        return self.bone_map
    
    def find_daz_bone_for_metarig_bone(self, metarig_bone_name):
        for mapping in self.bone_map:
            if mapping[1] == metarig_bone_name:
                return mapping[0]
        return None

    def find_rigify_bone_for_daz_bone(self, daz_bone_name):
        for mapping in self.bone_map:
            if mapping[0] == daz_bone_name:
                return mapping[2]
        return None
    
    def find_vertex_group_to_merge_to(self, daz_vertex_group, use_fewer_bones=False):
        if use_fewer_bones:
            for (key_world, daz_bone, symmtrize) in self.daz_vertex_group_merge_less_bone_map:
                if key_world in daz_vertex_group:
                    if symmtrize:
                        daz_bone = daz_vertex_group[0] + daz_bone
                    return daz_bone

        # never merge a bone there is already a matching rigify bone
        if self.find_rigify_bone_for_daz_bone(daz_vertex_group) != None:
            return None
        
        for (key_world, daz_bone, symmtrize) in self.daz_vertex_group_merge_map:
            if key_world in daz_vertex_group:
                if symmtrize:
                    daz_bone = daz_vertex_group[0] + daz_bone
                return daz_bone
        return None

def merge_vertex_group(from_group, to_group):
    object = bpy.context.object
    if from_group not in object.vertex_groups:
        raise Exception('no vertex group exist for ' + from_group)
    if to_group not in object.vertex_groups:
        raise Exception('no vertex group exist for ' + to_group)
    
    merge_modifer = object.modifiers.new(name="Merge Vertex Groups", type='VERTEX_WEIGHT_MIX')
    merge_modifer.vertex_group_a = to_group
    merge_modifer.vertex_group_b = from_group
    merge_modifer.mix_mode = 'ADD'
    merge_modifer.mix_set = 'OR'
    
    bpy.ops.object.modifier_apply(modifier=merge_modifer.name)
    object.vertex_groups.remove(object.vertex_groups.get(from_group))

class Rigify2Daz_PT_Panel(bpy.types.Panel):
    bl_label = "Match metarig to Genesis 8 rig"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(self, context):
        return bpy.context.object.type == 'ARMATURE' and bpy.context.object.pose.bones.get('spine') != None and bpy.context.object.pose.bones.get('spine.001') != None
    
    def draw(self, context):
        self.layout.prop(context.object.data, "genesis_8_rig", text="Genesis 8")
        self.layout.prop(context.object.data, "use_fewer_bones", text="Use Fewer Bones")
        self.layout.operator("vsw.metarig2genesis8")

def set_bone_location(bone, head, tail):
    if head:
        bone.head.x = head.x
        bone.head.y = head.y
        bone.head.z = head.z
    if tail:
        bone.tail.x = tail.x
        bone.tail.y = tail.y
        bone.tail.z = tail.z


class MatchMetaRigToGenesis8Rig(bpy.types.Operator):
    bl_idname = "vsw.metarig2genesis8"
    bl_label = "Match"
    mapper = DazRigifyBoneMapper()

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        current_rig = bpy.context.object
        genesis_8_rig = current_rig.data.genesis_8_rig
        use_fewer_bones = current_rig.data.use_fewer_bones
        genesis_8_rig.data.pose_position = 'POSE'

        for bone in current_rig.data.edit_bones:
            genesis_8_bone_name = self.mapper.find_daz_bone_for_metarig_bone(bone.name)
            if (genesis_8_bone_name == None):
                continue
            
            genesis_8_bone = genesis_8_rig.pose.bones.get(genesis_8_bone_name)
            head = genesis_8_bone.head
            tail = genesis_8_bone.tail
            
            if (genesis_8_bone_name == 'pelvis'):
                temp = head
                head = tail
                tail = temp
            
            set_bone_location(bone, head, tail)
        
        if use_fewer_bones:
            # fix chest
            set_bone_location(
                current_rig.data.edit_bones.get('spine.003'),
                genesis_8_rig.pose.bones.get('abdomenUpper').tail,
                genesis_8_rig.pose.bones.get('neckLower').head)
            
            # fix neck
            set_bone_location(
                current_rig.data.edit_bones.get('spine.004'),
                genesis_8_rig.pose.bones.get('neckLower').head,
                genesis_8_rig.pose.bones.get('neckUpper').tail)
            
            # fix head in case it got moved
            set_bone_location(
                current_rig.data.edit_bones.get('spine.005'),
                genesis_8_rig.pose.bones.get('head').head,
                genesis_8_rig.pose.bones.get('head').tail)

        else:
            # connect chest bone to neck bone
            upper_chest_bone = current_rig.data.edit_bones.get('spine.006')
            neck_head = current_rig.data.edit_bones.get('spine.004').head   
            set_bone_location(upper_chest_bone, None, neck_head)

        return{'FINISHED'}

class MatchRigifyVertexGroup_Panel(bpy.types.Panel):
    bl_label = "Rename Genesis 8 Vertex Groups to Rigify"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(self, context):
        return bpy.context.object.type == "MESH"
    
    def draw(self, context):
        self.layout.operator("vsw.genesis8vert2rigify")
        self.layout.prop(context.object.data, "use_fewer_weights", text="Use Fewer Bones")

class RenameGenesis8VertexGroupsToRigify(bpy.types.Operator):
    bl_idname = "vsw.genesis8vert2rigify"
    bl_label = "Match Rigify Vertex Groups"
    mapper = DazRigifyBoneMapper()

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = bpy.context.object
        use_fewer_weights = obj.data.use_fewer_weights

        # apply the pose as rest position
        bpy.ops.object.modifier_apply(modifier='Armature')

        # get rid of all the modifiers
        for modifier in obj.modifiers:
            obj.modifiers.remove(modifier)

        for (name, group) in obj.vertex_groups.items():
            merge_bone = self.mapper.find_vertex_group_to_merge_to(name, use_fewer_weights)
            if merge_bone == None:
                continue
            merge_vertex_group(name, merge_bone)

        # rename vertex groups
        for (name, group) in obj.vertex_groups.items():
            new_name = self.mapper.find_rigify_bone_for_daz_bone(name)
            
            if new_name == None:
                raise Exception('unmapped bone: ' + name)

            obj.vertex_groups.get(name).name = new_name

        return{'FINISHED'}

def register():
    utils.register_quietly(Rigify2Daz_PT_Panel)
    utils.register_quietly(MatchMetaRigToGenesis8Rig)
    utils.register_quietly(MatchRigifyVertexGroup_Panel)
    utils.register_quietly(RenameGenesis8VertexGroupsToRigify)

    bpy.types.Armature.genesis_8_rig = PointerProperty(type=bpy.types.Object,
        name="Genesis 8 Rig",
        description="Genesis 8 Target Rig",
        poll=lambda self, obj: obj.type == 'ARMATURE' and obj.data is not self)

    bpy.types.Armature.use_fewer_bones = BoolProperty(
        name="Use Fewer Bones",
        description="Genesis 8 Rig has more chest/neck bones than standard rig, use this option to reduce the bones",
        default=False)

    bpy.types.Mesh.use_fewer_weights = BoolProperty(
        name="Use Fewer Bones",
        description="Genesis 8 Rig has more chest/neck bones than standard rig, use this option to reduce the bones",
        default=False)

def unregister():
    utils.unregister_quietly(Rigify2Daz_PT_Panel)
    utils.unregister_quietly(MatchMetaRigToGenesis8Rig)
    utils.unregister_quietly(MatchRigifyVertexGroup_Panel)
    utils.unregister_quietly(RenameGenesis8VertexGroupsToRigify)

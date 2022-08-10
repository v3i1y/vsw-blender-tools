# Blender Tools
Repository for some blender-addons I wrote for myself only. I don't mind you using them if you bump into this repo randomly and find these scripts helpful.

## bind_metarig_to_rigify_rig

This is a tool that binds the rigify metarig to the generated rig. So that when we use the control bones to control the generted rig the metarig moves with it.

The purpose is so that we can bind and weight paint the mesh to the metarig instead of the deform bones of the generated rig. This is helpful for exporting the rig to game engines since the meta rig is much cleaner and you don't have to edit out the extra deform bones that the rigify rig genertes by default. Yet you still have the versatile control of the generated rigify rig if you every need to pose or animate the character.

## bind_genesis8_with_rigify

This is a tool that allows binding Daz 3D Genesis 8 mesh to a rigify rig. The Gensis 8 mesh needs to be imported with the official Daz to Blender addon.

The reason for this is that I think posing in blender with rigify rig is a lot more easier than Daz 3D's controls... plus the benefits of being able to have some nice renders in real time. The only downside being that you don't get the nice muscle deforms that Daz's engine came with.

It works by renaming all the vertex groups of a Genesis 8 mesh to much the deform bones of a rigify rig.

## Step 0
The daz figure needs to be posed a little bit for rigify to generates to correct IK. This means that all the joints including fingers need to be bent to the correct direction just by a little bit. Once posed, export it to blender.

## Step 1
You need a metarig that's placed properly inside a genesis 8 mesh. This is done by simply match the position of a genesis 8 metarig to the positions of the Genesis 8 rig exported from Daz.

Worth noting that Daz has more spine and neck bones than default metarig. This can be fixed by either adding those extra bones to the metrig:

basic spine
```
spine -> spine.001 -> spine.002 -> spine.003 -> **spine.004**
```
super head
```
spine.004 -> **spine.007** -> spine.005
```

Can also be fixed by ticking the fewer bones option so that it tries to still use the existing bones instead of added bones.

## Step 2
Apply the armature deforms to the Daz figure. And then use the apply the rename in the Data panel of blender. This has a corresponding fewer bones option too.

## Step 3
Generate the rigify rig and apply armature deform to the Daz figure with renamed vertex group to it.


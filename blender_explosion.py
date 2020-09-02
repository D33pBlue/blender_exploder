#######################################################################################
# Copyright 2020 - d33pblue
#
# Simple Blender plugin for mesh explosion along faces' normals.
#
# In order to run once you can include this file in Blender and execute it.
# In order to install this plugin you can:
#  - Open the Preferences ‣ Add-ons ‣ Install… and select the file.
#  - Now the add-on will be listed and you can enable it by pressing the checkbox, 
#    if you want it to be enabled on restart, press Save as Default.
#
# Once the plugin is installed you can find the function "Explode Mesh On Normals"
# searching for it with the search tool, or inside the object menu.
#######################################################################################

# these informations are required by Blender to install the plugin
bl_info = {
    "name": "Explode Mesh On Normals",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import bmesh

class ExplodeMeshOnNormals(bpy.types.Operator):
    """Explode Mesh On Normals"""
    bl_idname = "object.explode_mesh_on_normals"
    bl_label = "Explode Mesh On Normals"
    bl_options = {'REGISTER', 'UNDO'}

    #this property can be tuned in Blender's UI
    factor: bpy.props.FloatProperty(name="Factor", default=0.5, min=-2, max=2)



    # this method actually performs the task
    def execute(self, context):
        # get a reference to the current selected object
        obj = context.active_object
        # get a reference to its mesh
        me = obj.data
        # dubplicate the mesh "without vertex indexing"
        destructable = self.duplicate_faces(obj,me)
        # apply the explosion transformation
        self.explode_destructable_obj(destructable,self.factor)
        # hide the original mesh
        obj.hide_set(True)
        return {'FINISHED'}
    


    # this method duplicate a mesh, keeping the faces detached (without vertex indexing)
    def duplicate_faces(self,orig,mesh):
        verts = []
        faces = []
        index = 0;
        # loop through the faces
        for p in mesh.polygons:
            # collect the vertices of each face
            face = []
            for v_ind in p.vertices:
                face.append(index)
                # update verts with the vertices (in world transform), eventually recreating the same
                # ones for each face that overlaps with others
                verts.append(orig.matrix_world @ mesh.vertices[v_ind].co)
                index += 1
            # update faces with the tuple that refers to the vertices of the current face
            faces.append(tuple(face))
        # create mesh data
        mesh_data = bpy.data.meshes.new("destructable_mesh_data")
        mesh_data.from_pydata(verts, [], faces)
        mesh_data.update()
        # create a new object and assign the mesh data
        obj = bpy.data.objects.new("Destructable", mesh_data)
        # update the scene
        scene = bpy.context.scene
        if bpy.app.version_string >= '2.8':
            scene.collection.objects.link(obj)
        else:
            scene.objects.link(obj)
        return obj
    


    # this method apply the transformations to the faces:
    # each face is translated by its normal multiplied by factor
    def explode_destructable_obj(self,obj,factor):
        me = obj.data
        # the transformation is applied through bmesh functions, that
        # slightly change if you are in edit mode or object mode
        if obj.mode == "EDIT":
            bm = bmesh.from_edit_mesh(me)
            for f in bm.faces:
                bmesh.ops.translate(bm,verts=f.verts,vec=factor*f.normal)
            bmesh.update_edit_mesh(me)
        else:
            bm = bmesh.new()
            bm.from_mesh(me)
            for f in bm.faces:
                bmesh.ops.translate(bm,verts=f.verts,vec=factor*f.normal)
            bm.to_mesh(me)
            me.update()



# this function adds the plugin to the object menu in Blender UI
def menu_func(self, context):
    self.layout.operator(ExplodeMeshOnNormals.bl_idname)


# this function registers the plugin in Blender
def register():
    bpy.utils.register_class(ExplodeMeshOnNormals)
    bpy.types.VIEW3D_MT_object.append(menu_func)

# this function unregisters the plugin in Blender
def unregister():
    bpy.utils.unregister_class(ExplodeMeshOnNormals)


# if you run the code in Blender, the plugin installs itself for the current session
if __name__ == "__main__":
    register()
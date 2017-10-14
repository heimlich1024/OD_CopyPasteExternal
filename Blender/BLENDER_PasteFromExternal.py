bl_info = {
    "name": "Paste From External",
    "version": (1, 0),
    "author": "Oliver Hotz",
    "description": "Paste from an external Object of other applications / instances to a current mesh",
    "category": "Object"
}

import bpy, tempfile, os
from mathutils import Vector
import bmesh

class PasteFromExternal(bpy.types.Operator):
    """Object Cursor Array"""
    bl_idname = "object.paste_from_external"
    bl_label = "Paste From External"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        def OD_PasteFromExternal(_name, size):

            file = tempfile.gettempdir() + os.sep + "ODVertexData.txt"

            if os.path.exists(file):
              f = open(file)
              lines = f.readlines()
              f.close()
            else:
                print("Cannot find file")

            vertline   = []
            polyline   = []
            uvMaps     = []
            morphMaps  = []
            weightMaps = []
            count      = 0
            #Parse File to see what Data we have here
            for line in lines:
              if line.startswith("VERTICES:"):
                vertline.append([int(line.strip().split(":")[1].strip()), count])
              if line.startswith("POLYGONS:"):
                polyline.append([int(line.strip().split(":")[1].strip()), count])
              if line.startswith("UV:"):
                uvMaps.append([line.strip().split(":")[1:], count])  # changed this to add the # of uv coordinates into the mix
              if line.startswith("MORPH"):
                morphMaps.append([line.split(":")[1].strip(), count])
              if line.startswith("WEIGHT"):
                weightMaps.append([line.split(":")[1].strip(), count])
              count += 1

            #create Points
            for v in vertline:
              verts = []
              for i in range(v[1] + 1, v[1] + v[0] + 1):
                x = lines[i].split(" ")
                pt = [ float(x[0].strip()), float(x[2].strip())*-1, float(x[1].strip()) ]
                verts.append(pt)

            blenderMats = bpy.data.materials[:]
            blenderMatsNames = []
            for bm in blenderMats:
              blenderMatsNames.append(bm.name)

            for polygons in polyline:
              faces = []
              facesMat = []
              objMats = []
              for i in range(polygons[1] + 1, polygons[1] + polygons[0] + 1):
                pts = []
                surf = (lines[i].split(";;")[1]).strip()
                for x in (lines[i].split(";;")[0]).strip().split(","):
                  pts.append(int(x.strip()))
                faces.append(pts)
                if surf not in blenderMatsNames:
                  blenderMatsNames.append(surf)
                  bpy.data.materials.new(surf)
                  #obj.data.materials.append(blenderSurf)
                if surf not in objMats:
                  objMats.append(surf)
                facesMat.append(surf)

            #remove old object first
            obj = bpy.context.active_object
            if obj != None:
                me = obj.data
                bpy.ops.object.mode_set(mode = 'OBJECT')
                facesr = me.polygons
                for f in facesr: f.select = 1
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.delete(type='FACE')
                bpy.ops.object.mode_set(mode = 'OBJECT')
                mesh = me
                mesh.from_pydata(verts, [], faces)
                mesh.update()
                mesh.update()
            else:
            # the rest keep like in this example
            # here the mesh data is constructed
                mesh = bpy.data.meshes.new(_name)
                mesh.from_pydata(verts, [], faces)
                mesh.update()
                mesh.update()
                # now generate an object to hold this data
                obj = bpy.data.objects.new(_name, mesh)
                # link the object to the scene (it is not visible so far!)
                bpy.context.scene.objects.link(obj)

            for i in range(len(obj.material_slots)):
              bpy.ops.object.material_slot_remove({'object': obj})
            for mat in objMats:
              obj.data.materials.append(bpy.data.materials.get(mat))

            for i in range(len(faces)):
              obj.data.polygons[i].material_index = objMats.index(facesMat[i])

            # create vertex group lookup dictionary for names
            vgroup_names = {vgroup.index: vgroup.name for vgroup in obj.vertex_groups}

            # create dictionary of vertex group assignments per vertex
            vgroups = {v.index: [vgroup_names[g.group] for g in v.groups] for v in obj.data.vertices}

            for x in obj.vertex_groups:
                obj.vertex_groups.remove(x)

            #setup  weightmaps
            for weightMap in weightMaps:
              vg = obj.vertex_groups.new(weightMap[0])
              count = 0
              for v in range(len(verts)):
                if lines[weightMap[1]+1+count].strip() != "None":
                  vg.add([v], float(lines[weightMap[1]+1+count].strip()), "ADD")
                count += 1

            if obj.data.shape_keys != None:
              bpy.ops.object.shape_key_remove(all=True)

            #create Base Shape Key
            if len(morphMaps) > 0:
              shapeKey = obj.shape_key_add(from_mix=False)
              #shapeKey.name = "Base"
              for vert in obj.data.vertices:
                shapeKey.data[vert.index].co = vert.co

            #Set Morph Map Values
            for morphMap in morphMaps:
              shapeKey = obj.shape_key_add(from_mix=False)
              shapeKey.name = morphMap[0]
              count = 0
              for vert in obj.data.vertices:
                if lines[morphMap[1]+1+count].strip() != "None":
                  x = float(lines[morphMap[1]+1+count].split(" ")[0])
                  y = float(lines[morphMap[1]+1+count].split(" ")[1])
                  z = float(lines[morphMap[1]+1+count].split(" ")[2])*-1
                  newVert = Vector((vert.co[0] + x, vert.co[1] + z, vert.co[2]+y))
                  shapeKey.data[vert.index].co = newVert
                count += 1

            for x in mesh.uv_textures:
                mesh.uv_textures.remove(x)

            for uvMap in uvMaps:
                uv = mesh.uv_textures.new(uvMap[0][0])
                bm = bmesh.new()
                bm.from_mesh(mesh)
                bm.faces.ensure_lookup_table()
                uv_layer = bm.loops.layers.uv[uv.name]

                count = 0
                for i in range(int(uvMap[0][1])):
                    line = lines[uvMap[1]+1+count]
                    split = line.split(":")
                    if len(split) > 3: #check the format to see if it has a point and poly classifier, determining with that, whether the uv is discontinuous or continuous
                        face = (bm.faces[int(split[2])].loops[count%(len(bm.faces[int(split[2])].loops))])[uv_layer].uv = [float(split[0].split(" ")[0]), float(split[0].split(" ")[1])]
                    else:
                        pass
                    count +=1
                bm.to_mesh(mesh)

            bpy.context.scene.update()

            # return the object to the function caller for further stuff
            return obj

        # call the function
        new_mesh = OD_PasteFromExternal('ODCopy', 1)
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(PasteFromExternal.bl_idname)

def register():
    bpy.utils.register_class(PasteFromExternal)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(PasteFromExternal)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()
bl_info = {
    "name": "Copy To External",
    "version": (1, 0),
    "author": "Oliver Hotz",
    "description": "Copies current object to clipboard for use in other applications / instances",
    "category": "Object"
}

import bpy, tempfile, os
from mathutils import Vector

class CopyToExternal(bpy.types.Operator):
    """Object Cursor Array"""
    bl_idname = "object.copy_to_external"
    bl_label = "Copy To External"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        def OD_CopyToExternal(_name, size):

            def mesh_to_weight_list(ob, me):
                # clear the vert group.
                group_names = [g.name for g in ob.vertex_groups]
                group_names_tot = len(group_names)
                if not group_names_tot:
                    # no verts? return a vert aligned empty list
                    return [[] for i in range(len(me.vertices))], []
                else:
                    weight_ls = [[0.0] * group_names_tot for i in range(len(me.vertices))]
                for i, v in enumerate(me.vertices):
                    for g in v.groups:
                        # possible weights are out of range
                        index = g.group
                        if index < group_names_tot:
                            weight_ls[i][index] = g.weight
                return group_names, weight_ls

            # get active object
            obj = bpy.context.active_object
            mesh = obj.data

            point_count = len(obj.data.vertices)
            poly_count = len(obj.data.polygons)

            file = tempfile.gettempdir() + os.sep + "ODVertexData.txt"
            f = open(file, "w")
            f.write ("VERTICES:" + str(point_count) + "\n")

            #write Vertices
            for vert in obj.data.vertices:
                f.write(str(vert.co[0]) + " " + str(vert.co[2]) + " " + str(vert.co[1]*-1) + "\n")

            #write polygons-point connection for poly reconstructions
            f.write("POLYGONS:" + str(poly_count) + "\n")
            for poly in obj.data.polygons:
                surf = "Default"
                if len(obj.material_slots)!= 0:
                    slot = obj.material_slots[poly.material_index]
                    surf = slot.name
                ppoint = ""
                polytype = "FACE"
                for idx in poly.vertices:
                    ppoint += "," + str(obj.data.vertices[idx].index)
                f.write(ppoint[1:] + ";;" + str(surf) + ";;" + polytype + "\n")

            #write all weights
            result1, result2 = mesh_to_weight_list(obj, mesh)
            if len(result1[0]) > 0:
                count = 0
                for weight in result1:
                    f.write("WEIGHT:" + weight + "\n")
                    for r in result2:
                        f.write(str(r[count]) + "\n")
                    count += 1

            #write all morphs
            for keys in bpy.data.shape_keys:
                for key in keys.key_blocks[1:]:
                    f.write("MORPH:" + key.name + "\n")
                    basis_verts = keys.key_blocks[0].data
                    for j, kv in enumerate(key.data):
                        delta = kv.co - basis_verts[j].co
                        f.write(str(delta[0]) + " " + str(delta[2]) + " " + str(delta[1]*-1) + "\n")

            #UVs
            for j, ul in enumerate(mesh.uv_layers):
                uv = []
                for poly in mesh.polygons:
                    for i in poly.loop_indices:
                        l = mesh.loops[i]
                        v = mesh.vertices[l.vertex_index]
                        uv.append([str(ul.data[l.index].uv[0]), str(ul.data[l.index].uv[1]), str(poly.index), str(l.vertex_index) ])
                f.write("UV:" + ul.name + ":" + str(len(uv)) + "\n")
                for entry in uv:
                    f.write(entry[0] + " " + entry[1] + ":PLY:" + entry[2] + ":PNT:" + entry[3] + "\n")

        # call the function
        new_mesh = OD_CopyToExternal('ODCopy', 1)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(CopyToExternal.bl_idname)

def register():
    bpy.utils.register_class(CopyToExternal)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(CopyToExternal)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()
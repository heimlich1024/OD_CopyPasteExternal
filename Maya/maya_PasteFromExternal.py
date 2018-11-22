import os
import pymel.core as pm
import maya.cmds as cmds
import tempfile
import maya.OpenMaya as om


class IObjectDef:
    name = ""
    vertexCount = 0
    vertexNormalsCount = 0
    polyCount = 0
    vertices = []
    polys = []
    materials = []
    weightMap = []
    vertexNormals = []
    omVertices = []
    loaded_data = []


def main():
    import_filename = tempfile.gettempdir() + os.sep + "ODVertexData.txt"
    import_object_name = "tempObject"

    global imported_object

    def load_object_from_text_file():
        global imported_object
        imported_object.loaded_data = []
        if not os.path.exists(import_filename):
            print("Cant find file")
            cmds.confirmDialog(
                title="Error:",
                message="Cant find file:\n" + import_filename,
                button="Ok",
            )
            return False
        else:
            f = open(import_filename)
            imported_object.loaded_data = f.readlines()
            f.close()
            return True

    def parse_text_data():
        global imported_object

        imported_object.name = "ODCOPY"

        # parse vertices:
        imported_object.vertexCount = int(
            imported_object.loaded_data[0].split(":")[1].strip()
        )
        imported_object.vertices = []
        imported_object.omVertices = []

        for v in range(1, imported_object.vertexCount + 1, 1):
            new_vert_string = imported_object.loaded_data[v].split(" ")
            new_vert = [
                float(new_vert_string[0]),
                float(new_vert_string[1]),
                float(new_vert_string[2].rstrip()),
            ]
            imported_object.vertices.append(new_vert)
            imported_object.omVertices.append(
                om.MPoint(new_vert[0], new_vert[1], new_vert[2])
            )

        # parse polys

        poly_line = -1
        count = 0

        for line in imported_object.loaded_data:
            if line.startswith("POLYGONS:"):
                poly_line = count
                break
            count += 1

        if poly_line == -1:
            cmds.confirmDialog(
                title="Error:",
                message="Error reading file\nNo polygons found!",
                button="Ok",
            )
            return False

        imported_object.polyCount = int(
            imported_object.loaded_data[poly_line].split(":")[1]
        )
        imported_object.polys = []
        imported_object.materials = []
        poly_line += 1

        for p in range(poly_line, poly_line + imported_object.polyCount, 1):
            new_poly_string = imported_object.loaded_data[p].split(";")[0].split(",")
            new_poly = []
            for vs in new_poly_string:
                new_poly.append(int(vs))
            imported_object.polys.append(new_poly)
            poly_material = imported_object.loaded_data[p].split(";")[2].rstrip()
            imported_object.materials.append(poly_material)

        # parse weights

        imported_object.weights = []
        weight_line = -1
        count = 0

        for line in imported_object.loaded_data:
            if line.startswith("WEIGHT:"):
                weight_line = count
                break
            count += 1

        if weight_line != -1:
            weight_line += 1
            for w in range(weight_line, weight_line + imported_object.vertexCount, 1):
                new_weight_string = imported_object.loaded_data[w].rstrip()
                imported_object.weightMap.append(float(new_weight_string))

        # Parse Vertex Normal Maps
        imported_object.vertexNormals = []
        _count = 0
        normal_line = -1
        for line in imported_object.loaded_data:
            if line.startswith("VERTEXNORMALS:"):
                imported_object.vertexNormalsCount = int(line.split(":")[2])
                normal_line = _count
            _count += 1

        if normal_line != -1:
            normal_line += 1
            for n in range(
                normal_line, normal_line + imported_object.vertexNormalsCount, 1
            ):
                values = imported_object.loaded_data[n].rstrip().split(":")
                polygon_id = values[2]
                vertex_id = values[4]
                normal_vector = tuple(float(x) for x in values[0].split(" "))
                imported_object.vertexNormals.append(
                    [normal_vector, polygon_id, vertex_id]
                )

        return True

    def create_object_openmaya():
        global imported_object

        cmds.select(all=True, hierarchy=True)
        current_objs = cmds.ls(selection=True)

        new_mesh = om.MFnMesh()

        merge_vertices = True
        point_tolerance = 0.0001

        # create polys
        for p in range(0, len(imported_object.polys), 1):
            poly_list = []
            v_count = len(imported_object.polys[p])
            poly_list = om.MPointArray()
            poly_list.setLength(v_count)
            for i in range(v_count):
                poly_list.set(
                    imported_object.omVertices[int(imported_object.polys[p][i])], i
                )
            new_mesh.addPolygon(poly_list, merge_vertices, point_tolerance)

        # create weightmaps
        if len(imported_object.weightMap) > 0:
            for v in range(0, imported_object.vertexCount, 1):
                c = imported_object.weightMap[v]
                vColor = om.MColor(c, c, c, c)
                new_mesh.setVertexColor(vColor, v)

        # Set mesh edits
        new_mesh.updateSurface()

        cmds.select(all=True, hierarchy=True)
        cmds.select(current_objs, deselect=True)
        mesh = pm.selected()[0]
        # create vertex normal map
        if len(imported_object.vertexNormals) > 0:
            for v in range(0, imported_object.vertexNormalsCount, 1):
                values = imported_object.vertexNormals[v]
                vertex_normal_vector = values[0]
                polygon_id = int(values[1])
                vert_id = int(values[2])
                try:
                    pm.select(mesh.vtxFace[vert_id][polygon_id])
                    pm.polyNormalPerVertex(xyz=vertex_normal_vector)
                except IndexError, e:
                    print e

        cmds.select(all=True, hierarchy=True)
        cmds.select(current_objs, deselect=True)
        new_objs = cmds.ls(selection=True, transforms=True)
        cmds.select(new_objs, replace=True)
        # cmds.sets(new_objs, e=True, forceElement="initialShadingGroup")
        cmds.rotate('90deg', 0, 0, r=True)
        pm.general.makeIdentity(apply=True, r=1)
        cmds.rename(new_objs, import_object_name)

    imported_object = IObjectDef()
    load_success = load_object_from_text_file()
    if load_success:
        parse_success = parse_text_data()
        if parse_success:
            create_object_openmaya()

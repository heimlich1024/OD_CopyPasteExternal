################################################################################
#
# paste_from_external.py
#
# Author: Oliver Hotz | Chris Sprance
#
# Description: Pastes Geo/Weights/Morphs/UV's from external file
#
# Last Update:
#
################################################################################
import lx
import modo
import tempfile
import os


def execute():
    scene = modo.Scene()
    # Read temporary Data File
    od_data_file = tempfile.gettempdir() + os.sep + "ODVertexData.txt"
    if os.path.exists(od_data_file):
        f = open(od_data_file, "r")
        lines = f.readlines()
        f.close()
        up_axis = {0: "x", 1: "y", 2: "z"}[scene.sceneItem.channel("upAxis").get()]
        vert_line = []
        poly_line = []
        uv_maps = []
        morph_maps = []
        weight_maps = []
        vertex_normals = []
        count = 0
        # Parse File to see what Data we have
        for line in lines:
            if line.startswith("VERTICES:"):
                vert_line.append([int(line.strip().split(":")[1].strip()), count])
            if line.startswith("POLYGONS:"):
                poly_line.append([int(line.strip().split(":")[1].strip()), count])
            if line.startswith("UV:"):
                uv_maps.append(
                    [line.strip().split(":")[1:], count]
                )  # changed this to add the # of uv coordinates into the mix
            if line.startswith("MORPH"):
                morph_maps.append([line.split(":")[1].strip(), count])
            if line.startswith("WEIGHT"):
                weight_maps.append([line.split(":")[1].strip(), count])
            if line.startswith("VERTEXNORMALS"):
                vertex_normals.append([line.split(":")[1].strip(), count])
            count += 1

        # Add a new mesh object to the scene and grab the geometry object
        mesh = scene.selectedByType("mesh")
        if mesh:
            mesh = mesh[0]
            if len(mesh.geometry.vertices) > 0:
                mesh.geometry.internalMesh.Clear()
        else:
            mesh = scene.addMesh("ODCopy")

        # select new empty mesh
        scene.select(mesh)
        geo = mesh.geometry

        # generate points
        for verts in vert_line:
            points = []
            for i in xrange(verts[1] + 1, verts[1] + verts[0] + 1):
                x = lines[i].split(" ")
                points.append(
                    geo.vertices.new((float(x[0]), float(x[1]), float(x[2].strip())))
                )

        # Query Existing Materials
        all_surfaces = []
        for material in scene.items("advancedMaterial"):
            all_surfaces.append(material.name)

        # generate Polys from the Points and assign materials
        for polygons in poly_line:
            polys = []
            count = 0
            for i in xrange(polygons[1] + 1, polygons[1] + polygons[0] + 1):
                pts = []
                surf = (lines[i].split(";;")[1]).strip()
                ptch = (lines[i].split(";;")[2]).strip()
                if surf not in all_surfaces:
                    all_surfaces.append(surf)
                    scene.addMaterial(name=surf)
                for x in (lines[i].split(";;")[0]).strip().split(","):
                    pts.append(int(x.strip()))
                ptype = lx.symbol.iPTYP_FACE
                if ptch == "CCSS":
                    ptype = lx.symbol.iPTYP_PSUB
                elif ptch == "SUBD":
                    ptype = lx.symbol.iPTYP_SUBD
                geo.polygons.new(vertices=(pts), reversed=False, polyType=ptype)
                geo.polygons[count].materialTag = surf
                count += 1

        # Apply Weights
        for weight_map in weight_maps:
            weight = geo.vmaps.addMap(lx.symbol.i_VMAP_WEIGHT, weight_map[0])
            for i in range(len(geo.vertices)):
                if lines[weight_map[1] + 1 + i].strip() != "None":
                    weight[i] = float(lines[weight_map[1] + 1 + i].strip())

        # Apply Morphs
        for morph_map in morph_maps:
            mo = geo.vmaps.addMorphMap(morph_map[0], False)
            for i in range(len(geo.vertices)):
                if lines[morph_map[1] + 1 + i].strip() != "None":
                    mo.setAbsolutePosition(
                        i,
                        [
                            float(lines[i + 1].split(" ")[0])
                            + float(lines[morph_map[1] + 1 + i].split(" ")[0]),
                            float(lines[i + 1].split(" ")[1])
                            + float(lines[morph_map[1] + 1 + i].split(" ")[1]),
                            float(lines[i + 1].split(" ")[2])
                            + float(lines[morph_map[1] + 1 + i].split(" ")[2]),
                        ],
                    )

        # Apply UV Maps
        for uv_map in uv_maps:
            uvm = geo.vmaps.addMap(lx.symbol.i_VMAP_TEXTUREUV, uv_map[0][0])
            count = 0
            for i in range(int(uv_map[0][1])):
                line = lines[uv_map[1] + 1 + count]
                split = line.split(":")
                # check the format to see if it has a point and poly classifier,
                # determining with that, whether the uv is discontinuous or continuous
                if len(split) > 3:
                    geo.polygons[int(split[2])].setUV(
                        (float(split[0].split(" ")[0]), float(split[0].split(" ")[1])),
                        geo.vertices[int(split[4])],
                        uvm,
                    )
                else:
                    pass
                count += 1

        # Apply Vertex Normals
        for vertex_normal in vertex_normals:
            normals = geo.vmaps.addVertexNormalMap(vertex_normal[0])
            line_number_start = vertex_normal[1]
            for i in range(int(lines[line_number_start].split(":")[2])):
                values = lines[line_number_start + 1 + i].split(":")
                normal_value = tuple(float(x) for x in values[0].split(" "))
                polygon = modo.MeshPolygon(int(values[2]), geo)
                for i in range(polygon.numVertices):
                    vert_number = int(values[4].replace("\n", ""))
                    normals.setNormal(
                        normal_value, modo.MeshVertex(vert_number, geo), polygon
                    )

        geo.setMeshEdits()
        vertex_normal_maps = mesh.geometry.vmaps.getMapsByType(lx.symbol.i_VMAP_NORMAL)
        lx.eval('select.vertexMap "%s" norm replace' % vertex_normal_maps[0].name)
        lx.eval("vertMap.convertToHardEdge false")
    else:
        print("No Data File Available.")

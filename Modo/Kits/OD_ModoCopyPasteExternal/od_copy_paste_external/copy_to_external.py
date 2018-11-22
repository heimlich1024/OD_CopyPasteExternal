################################################################################
#
# copy_to_external.py
#
# Author: Oliver Hotz | Chris Sprance
#
# Description: Copies Geo/Weights/Morphs/UV's to External File
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
    # Setup File/path to where we store the temporary Data
    file = tempfile.gettempdir() + os.sep + "ODVertexData.txt"

    fusion = 0
    replicator = 0
    selmeshes = scene.selected
    if selmeshes[0].type == "mesh":
        selmeshes = selmeshes
    elif selmeshes[0].type == "sdf.item":
        fusion = 1
        # get original name
        itemname = selmeshes[0].name
        # duplicate meshfusion item
        lx.eval("item.duplicate false locator false true")
        # select original meshfusion item
        scene.select(selmeshes[0])
        # convert original meshfusion item to mesh, as we cannot convert the duplicate
        # - creates empty item on duplicate
        lx.eval("item.setType mesh sdf.item")
        selmeshes = scene.selected
    elif selmeshes[0].type == "replicator":
        replicator = 1
        itemname = selmeshes[0].name
        lx.eval("item.duplicate false locator false true")
        new = scene.selected
        # freeze Replicators
        lx.eval("replicator.freeze")
        # select whole Hierarchy
        scene.select(new[0].name + " (2)")
        lx.eval("select.itemHierarchy")
        # convert to mesh
        lx.eval("item.setType mesh locator")
        lx.eval("layer.mergeMeshes true")
        selmeshes = scene.selected

    if len(selmeshes) > 0:
        mesh = selmeshes[0]
        geo = mesh.geometry

        # Deselect all Morphs
        lx.eval("vertMap.list morf _____n_o_n_e_____")

        if len(geo.vertices) > 0:
            f = open(file, "w")
            # write Header
            f.write("VERTICES:" + str(len(geo.vertices)) + "\n")
            # Write Point/Vertex Position
            points = []
            for i in range(len(geo.vertices)):
                pos = geo.vertices[i].position
                points.append(geo.vertices[i])
                f.write(str(pos[0]) + " " + str(pos[1]) + " " + str(pos[2] * 1) + "\n")

            # Write Polygons
            f.write("POLYGONS:" + str(len(geo.polygons)) + "\n")
            for p in range(len(geo.polygons)):
                surf = geo.polygons[p].materialTag
                ptype = geo.polygons[p].Type()
                polytype = "FACE"
                if ptype == lx.symbol.iPTYP_PSUB:
                    polytype = "CCSS"
                elif ptype == lx.symbol.iPTYP_SUBD:
                    polytype = "SUBD"

                ppoint = ""
                for vert in geo.polygons[p].vertices:
                    ppoint += "," + str(vert.index)
                f.write(ppoint[1:] + ";;" + surf + ";;" + polytype + "\n")

            # WeightMaps:
            weightMaps = mesh.geometry.vmaps.weightMaps
            for weightMap in weightMaps:
                f.write("WEIGHT:" + weightMap.name + "\n")
                for i in range(len(geo.vertices)):
                    weight = weightMap[i]
                    if weight != None:
                        f.write(str(weight[0]) + "\n")
                    else:
                        f.write("None\n")

            # MorphMaps
            morphMaps = mesh.geometry.vmaps.morphMaps
            for morphMap in morphMaps:
                f.write("MORPH:" + morphMap.name + "\n")
                for i in range(len(geo.vertices)):
                    morph = morphMap[i]
                    if morph != None:
                        f.write(
                            str(morph[0])
                            + " "
                            + str(morph[1])
                            + " "
                            + str(morph[2])
                            + "\n"
                        )
                    else:
                        f.write("None\n")

            # UVMaps
            uvMaps = mesh.geometry.vmaps.uvMaps
            for uvMap in uvMaps:
                uvs = []
                for p in range(len(geo.polygons)):
                    for vert in geo.polygons[p].vertices:
                        uvs.append([geo.polygons[p].getUV(vert, uvMap), p, vert.index])
                f.write("UV:" + uvMap.name + ":" + str(len(uvs)) + "\n")
                for uv in uvs:
                    f.write(
                        str(uv[0][0])
                        + " "
                        + str(uv[0][1])
                        + ":PLY:"
                        + str(uv[1])
                        + ":PNT:"
                        + str(uv[2])
                        + "\n"
                    )

            # vertex Normal
            vertexnormals = []
            for p in range(len(geo.polygons)):
                for index, vert in enumerate(geo.polygons[p].vertices):
                    vertexnormals.append(
                        [geo.polygons[p].vertexNormal(index), p, vert.index]
                    )
            f.write(
                "VERTEXNORMALS:"
                + str('VertexNormals')
                + ":"
                + str(len(vertexnormals))
                + "\n"
            )
            for normal in vertexnormals:
                f.write(
                    str(normal[0][0])
                    + " "
                    + str(normal[0][1])
                    + " "
                    + str(normal[0][2])
                    + ":PLY:"
                    + str(normal[1])
                    + ":PNT:"
                    + str(normal[2])
                    + "\n"
                )

        # close File
        f.close()
    else:
        modo.dialogs.alert(
            "No Mesh Selected",
            "You need to select the mesh Item you want to copy",
            "info",
        )

    if fusion == 1 or replicator == 1:
        # delete converted item
        scene.removeItems(scene.selected[0])
        # select the duplicated meshfusion item
        x = scene.select(itemname)
        # change name of of the duplicate to the original meshfusion name
        scene.selected[0].SetName(itemname)

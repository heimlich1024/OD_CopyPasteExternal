# OD_CopyPasteExternal
Easily copying and pasting of geometry between 3D Applications

# General Information:

- Copy To External: will copy the current mesh into memory
- Paste From External: will rebuild the geometry thats in memory

The following applications are supported:

Modo      : Vertices / Polygons (incl. Subpatch and SubD)/ WeightMaps / UVMaps / MorphMaps

Lightwave : Vertices / Polygons (incl. Subpatch and SubD)/ WeightMaps / UVMaps / MorphMaps

Blender   : Vertices / Polygons (incl. Subpatch and SubD)/ WeightMaps / UVMaps / MorphMaps

Maya      : Vertices / Polygons / Weights (via Vertex Normals)

Houdini   : Vertices / Polygons / Weightmaps, UVMaps

Cinema4D  : None (looking for people to contribute)

3dsMax    : None (looking for people to contribute)

XSI		    : None (looking for people to contribute)


### MODO Install:

Drag the OD_ModoCopyPasteExternal folder into your kits folder.
Upon Modo start/restart you now have two additional commands:

OD_CopyToExternal & OD_PasteFromExternal

You can map them into your menu or hotkeys via the forms/input editor.

### LIGHTWAVE Install (2015+):

Add the LW_CopyPasteExternal.py via add plugins. 3 Plugins should be added:

in Layout: OD_LayoutPasteFromExternal
in Modeler: OD_LWPasteFromExternal & OD_LWCopyToExternal

Add them to the menus as you please.

Steve White has provided a Youtube Video here showing the use between Modo and Lightwave.

<a href="http://www.youtube.com/watch?feature=player_embedded&v=6jKi34irylo
" target="_blank"><img src="http://img.youtube.com/vi/6jKi34irylo/0.jpg"
alt="LW-Modo Usage" width="240" height="180" border="10" /></a>
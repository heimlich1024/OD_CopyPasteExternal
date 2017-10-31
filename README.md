# OD_CopyPasteExternal
Easily copying and pasting of geometry and common atributes across 3D Applications, perfect for quick iterations between them, without concerns about file management.              [Quick Download](https://github.com/heimlich1024/OD_CopyPasteExternal/archive/master.zip)

# Why ?

Because quite frankly nothing this easy exists.  And if you are like me working in environments using
multiple applications, this becomes extremely beneficial.  I opensourced it, in the hope, that there are other
people willing to contribute, in applications that I have either a) not touched, or b) have not as much experience
in to make this even better than it already is.  So if you are willing to contribute, please get in touch with me.

Currently, it uses an always existing temporary directory to store the intermediate custom file on the local machine,
but of course that directory can be changed to live on a dropbox (for online internet sharing with friends), or on a
network server for inter company sharing.  Those are really just some of the possibilies.

# Help ?

If you want to help and contribute, please get in touch with me.  There's XSI, Cinema4D and 3dsMax that still need
to be done, as well as the Houdini Exporter.  So anyone with experience in the SDK on those apps, please take a look.

# General Information:

* Copy To External: will copy the current mesh into memory
* Paste From External: will rebuild the geometry thats in memory

The following applications are supported:

* Modo      : Vertices / Polygons (incl. Subpatch and SubD)/ WeightMaps / UVMaps / MorphMaps
* Lightwave : Vertices / Polygons (incl. Subpatch and SubD)/ WeightMaps / UVMaps / MorphMaps
* Blender   : Vertices / Polygons (incl. Subpatch and SubD)/ WeightMaps / UVMaps / MorphMaps
* Maya      : Vertices / Polygons / Weights (via Vertex Normals) (Implementation by Andre Hotz)
* Houdini   : Vertices / Polygons / Weightmaps / VMaps
* C4D : Vertices / Polygons / UVs
* Rhino		: Vertices / Polygons (should be a good starting point for someone more experienced to finish it)
* Sketchup  : Vertices / Polygons (Paste only for now - Initial implementation provided as starting point)
* 3DsMax 	: Vertices / Poyygons (Initial implementation provided as a starting point)
* XSI   : Vertices / Polygons / WeightMaps / Morphs
* Moi3D : Vertices / Polygons
* ZBrush : Vertices / Polygons / UVs
* Substance Painter : Vertices / Polygons / UVs
* 3D-Coat: Vertices / Polygons / UVs
* Unity: Vertices/ Polygons / UVs / Materials
* Mari : Vertices / Polygons / UVs (in beta)
* Others	: Looking for contributors to write implementations for other 3d Apps (see TODO)

# Installation:

### MODO Install (tested 10.01 and higher):

Drag the OD_ModoCopyPasteExternal folder into your kits folder.
Upon Modo start/restart you now have two additional commands:

OD_CopyToExternal & OD_PasteFromExternal

You'll see a Scissors Icon in your Tailbar which includes those commands.

### LIGHTWAVE Install (2015+):

Add the LW_CopyPasteExternal.py via add plugins. 3 Plugins should be added:

in Layout: OD_LayoutPasteFromExternal
in Modeler: OD_LWPasteFromExternal & OD_LWCopyToExternal
Add them to the menus as you please.

### Maya Install

Just install the two scripts as any other plugin.

### Blender Install (tested 2.78c)

Preferences/Addons/Install from File and select the files and click the checkbox.
The plugins are then found under the object menu.

### Houdini Install (tested 15 and higher)

Start Houdini and Right Click on an empty space in the shelf and select New Tool.
Then go to the Scrips Tab and paste the contents of the python file there.  In the
options tab, you can name the tools, click apply and accept, and you are good to go.

### Rhino Install (V5+)

Preliminary Python scripts to be put in the script editor and launch accordingly

### 3DS Max (tested 2015+)

Preliminary Paste script to be called from the Max Script Editor (see .py for instructions)

### Sketchup

Copy the contents of the paste script into the Ruby Console Window in Sketchup

### ZBrush

Copy the contents of the ZBrush folder in the download into the ZStartup/ZPlugs64 folder.
So in the ZStartup/ZPlugs64 you should have the ODCopyPaste folder and also the zscript file.
For x32 versions of windows, just drop the "64" from the folders above.
For OSX versions, unzip the OSX Binaries into the same folder.

### Substance Painter

Within Substance painter, under plugins, select get plugins folder.  Copy the contents of the
SubstancePainter folder contained in this distribution into that folder.  You can then
Reload the plugins in substance painter, which will give you a PasteExt button.  Only import
is working, as exporting is irrelevant (there are no model changes within Painter).  Currently
only windows is supported, however, doing the same implementation for OSX shouldn't be hard.

### 3D-Coat (Windows Only)

To Install, copy these files into the scripts folder in your 3dCoat documents folder.
Here, it is C:\Users\username\Documents\3D-CoatV47\Scripts.  Should you not have a
Scripts folder there, just copy the entire folder, otherwise, make a folder, in put the
files in there.
In 3DCoat, under the scripts tab, select Run Script, and select the two .txt files contained
here.  From that point on, they'll show up under the Script Menu and you can use them as is.

### Maxon Cinema 4D

Copy the plugins into the scripts folder and they should show up under the python menu. You
might have to manually run them the first time.  This current implementation is a holdover
until the proper C4D C implementation can be finished.  It currently only supports Points,
Polygons and UV's and brings up the OBJ requester on "PasteFromExternal"

### Moi 3D

Copy the contents of the Moi3D folder into the commands folder of your Moi Installation.
You can then call the scripts via hotkeys, or the external script manager if you have it.

### XSI

Open the script editor within XSI and load the script, make a new shelf, and then drag the
script to the shelf, and setup a button.  Do that for both copy/paste scripts

### UNITY

Two new menu items are added:

[MenuItem("Edit/Paste Mesh from External %#v")]
[MenuItem("Edit/Copy Mesh To External %#c")]

Deleting pasted meshes will leak in editor (but adding a DestroyImmediate will break Undo...). A fix probably means creating meshes as project assets instead of scene instances.
At the moment meshes are assumed to be in left handed coordinates. Export has a way to change this, but import does not.
Multiple meshes aren't exported, only the first selected. In the future it would be nice to merge multiple meshes.
Morph targets aren't imported.
Import always triangulates meshes. Unity does support Quads, so it would be nice to keep that topology where possible.

# FAQ
* How do I report an issue ?

  Go to the Issues tab in GitHub, and open a new ticket.  Its helpful if you can attach the ODVertData.txt that will
  have been created in your temp folder.  Please also state the applications that you are going in between and which application the error occurs.
* How do I change where the temporary file is stored ?

  While you should not have to change the path (the nice thing is that its a worryfree setup) you can open the .py scripts
  in a text editor, and adjust the line where I define the file for ODVertData.txt
* Why are you not using obj, fbx or alembic ?

  Simply because simplicity.  I choose the ASCII format so that any app and any person can look at the data, and write a parser
  if need be.  Doing this via alembic or fbx makes it much more difficult, and there's quite a few applications that don't support
  alembic/etc.  Also, there's applications that use javascript or ruby, which, it would be a lot more work to make them function.
  This concept is not about asset transfering.  While i want to preserve as UV's, weights, morphs, etc, its is not about maintaining
  poses, relationships, scenedata, etc.  It is simply about providing a brainless "fire & forget" approach to quick move an object
  between apps.  Think of it more along the lines of what GoZ does for zbrush, or the applink mechanism of 3DCoat.
* I looked at the code, and there's stuff in there that could definintely be cleaned up and made more "proper".  Would you be offended
  if I take a stab at it ?

  I wouldn't be offended at all.  Please by all means, thats why I open-sourced this project so that people would take a look, make it
  better, come up with cleverer ways to provide such needed workflows.  So If you feel that you have a better approach to the data in
  Maya, or other apps, please feel free.  Contribute !


# Tutorials & Videos

Steve White has provided a Youtube Video here showing the use between Modo and Lightwave.

<a href="http://www.youtube.com/watch?feature=player_embedded&v=6jKi34irylo
" target="_blank"><img src="http://img.youtube.com/vi/6jKi34irylo/0.jpg"
alt="LW-Modo Usage" width="240" height="180" border="10" /></a>

Pedro Alpiarça dos Santos has provided a Youtube Video showing the use between Houdini, Blender and Lightwave.

<a href="http://www.youtube.com/watch?feature=player_embedded&v=PFFQxb3nMvw
" target="_blank"><img src="http://img.youtube.com/vi/PFFQxb3nMvw/0.jpg"
alt="Houdini-Blender-Lightwave Usage" width="240" height="180" border="10" /></a>

Steve Gilbert has provided a Youtube Video showing the use between 3DSMax and Blender.

<a href="http://www.youtube.com/watch?feature=player_embedded&v=ATWYuD7uHxg
" target="_blank"><img src="http://img.youtube.com/vi/ATWYuD7uHxg/0.jpg"
alt="3DSMax-Blender Usage" width="240" height="180" border="10" /></a>

# TODO:

* Houdini:  figure out how to get Morphs/Blendshapes integrated
* Maya:     figure out how to get Morphs/Blendshapes integrated
* Cinema4d: C Implementation (currently only python (vertices,polys,uvs supported))
* 3DsMax:   Initial Implementation as sample is complete
* Sketchup: Add Copy To and finesse Paste implementation
* Unreal:   R&D to see if its possible to implement
* Unity:    R&D to see if its possible to implement
* Mari:    R&D to see if its possible to implement
* Nuke:    R&D to see if its possible to implement

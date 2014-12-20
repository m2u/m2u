m2u
===
m2u is a collection of modular python scripts and plugins to allow for interactive syncing of "level building data" between 3D-Authoring-Applications (*Programs*) and Game-Engine-Applications (*Editors*).

Currently only Maya and Unreal Engine 4 are supported. A Unity plugin is in the works and hopefully we will be able to add a 3DsMax implementation some day.

To get an Idea of what m2u can do:
- https://vimeo.com/101552170
- https://vimeo.com/102053975
- https://vimeo.com/103139039

You can also take a look at the [development thread in the UE4 forums](https://forums.unrealengine.com/showthread.php?22515-m2u-interactive-sync-script-for-Maya-gt-UE4).

Using the script in Maya
---
1. Check out the **develop** branch. (The master branch will only be updated when we have a set of features working, mostly bug-free, but is currently very outdated.)
2. Make sure that Maya can find it. This means the folder above the m2u folder has to be listed in the python path. You can do that by executing `sys.path.append("path/to/folder_above_m2u")` or by using the environment variable `PYTHONPATH`. In a managed environment (Pipeline) this is often overridden when starting Maya through a shell script or .bat file (if you don't know what you should do, ask your TD/TA about it).
3. Start m2u by executing
```python
import m2u
m2u.core.initialize("maya","ue4")
m2u.core.getProgram().ui.createUI()```
And then hit the connect button with the Editor running and listening.

**NOTE:** You will have to use Z-up space in Maya currently.

Feature Status:
---
working:
- syncing the persp viewport camera
- fast fetching selected objects from the Editor (uses ExportSelected to single FBX file)
- syncing transforms of objects (now correct even with modified pivots)
- duplicating of objects
- hiding/showing of objects (due to the nature of how isolate select works in maya, this may not always be 100% correct)
- deleting objects
- renaming objects (unused and used names)
- syncing display layers (a bit buggy sometimes)

work in progress:
- a modular pySide based UI (some of the pipeline-tasks depend on this)
- allow and auto-detect Maya-Y-up space
- getting 'known' meshes from the file system (importing the fbx file associated with a static mesh by checking the project structure on the file system. This allows to build levels in maya, and send the whole stuff to UE at once)
- sending 'new' meshes from maya to UE (export to fbx, create asset, place in level. Thought further, this allows to quickly edit meshes and get the changes in the engine with one click)
- getting 'unknown' meshes which are not on the file system but exist as static meshes in UE 
- parenting and grouping of objects
- support for other objects than meshes (namely lights)
- making mass operations like selection and duplication faster (currently only one operation per tick)

to be investigated some day (no idea when I will come to this):
- transferring collision data (UCX prefixed meshes)
- transferring dependent textures (automatically import/export)
- sending skeletal mesh posing data (interactively get posing response in engine viewport when editing animations in maya)
- syncing cameras on playback (for creating camera paths in maya and seeing an interactive preview in the editor)
- two way interactive sync for simple stuff like selection (select something in UE will select the same in Maya)
- ...

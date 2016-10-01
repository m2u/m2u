m2u
===
m2u is a collection of modular python scripts and plugins to allow for interactive syncing of "level building data" between 3D-Authoring-Applications (*Programs*) and Game-Engine-Applications (*Editors*).

Currently only Maya and Unreal Engine 4 are supported.

To get an Idea of what m2u can do:
- https://vimeo.com/101552170
- https://vimeo.com/102053975
- https://vimeo.com/103139039

You can also take a look at the [development thread in the UE4 forums](https://forums.unrealengine.com/showthread.php?22515-m2u-interactive-sync-script-for-Maya-gt-UE4).

Using m2u in Maya
---
1. Clone or download the repository (hit the green button on the top-right of this page).

    > Note: If you download the .zip, it will have the branch- or tag-name in the file-name like `m2u-develop`. After unzipping, make sure that the folder is only called `m2u`, or this won't work.
	
2. Put the m2u folder into a place where Maya can find it. This means the folder **above** the m2u folder has to be listed in the [python sys-path](https://docs.python.org/2/library/sys.html#sys.path). 

    There are multiple ways to achieve this:

    * You can add temporarily to the sys-path by [executing](http://help.autodesk.com/view/MAYAUL/2016/ENU//?guid=GUID-7C861047-C7E0-4780-ACB5-752CD22AB02E):

      ```python
      import sys
      sys.path.append("path/to/folder_above_m2u")
      ```

    * Maya will by default look for scripts in a few directories, among others `<user’s directory>/My Documents/maya/scripts` and `<maya_directory>/scripts/others`. See the **PYTHONPATH** section on the [Knowledge Network](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2015/ENU/Maya/files/Environment-Variables-File-path-variables-htm.html) for more info. If you put m2u in any of these directories, Maya should be able to find it.

    * You can also modify (or create) the [PYTHONPATH environment variable](https://docs.python.org/2/using/cmdline.html#envvar-PYTHONPATH). Add an entry that points to the directory above the m2u directory, and every python on your system should be able to find m2u. 
    
	  > Note: In a managed environment (pipeline) this is often overridden when starting Maya through a shell script or .bat file. If you don't know what you should do, ask your pipeline-team / Technical Director about it.
	
3. Start m2u by [executing](http://help.autodesk.com/view/MAYAUL/2016/ENU//?guid=GUID-7C861047-C7E0-4780-ACB5-752CD22AB02E):

    ```python
    import m2u
    m2u.core.initialize("maya","ue4")
    m2u.core.program.ui.create_ui()
    ```

4. Make sure the *Editor* is running and has the *m2uPlugin* loaded. Hit the connect button in the m2u window. If that went successfull, select what you want to be synced and have fun.

    > You might want to click the *Setup Cameras* button to adapt Maya's cameras to large-scale scenes and 90˚ FOV.
	

> Note: You will currently have to use [**Z-up**](http://help.autodesk.com/view/MAYAUL/2016/ENU//?guid=GUID-4FDF34B0-D51B-48C2-8651-EC33127DD8E6) space in Maya.

License
---
MIT

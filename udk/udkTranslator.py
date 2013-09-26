# translates objects n stuff into udk textformat and the other way round


#from Tkinter import Tk
#clipboard = Tk()

#clipboard.withdraw()
#clipboard.clipboard_clear()
#clipboard.clipboard_append('i can has clipboardz?')
#clipboard.destroy()
#clipboard.clipboard_get()


#from helper.ObjectInfo import ObjectInfo


def meshToText():
    """
    converts a mesh info to UDK static mesh text
    """
    pass

def extractMeshSig(text = "", fromClipboard = True):
    """
    get the mesh signature from a static mesh text
    packagename.groupname.meshname in one string
    """
    if text=="" and fromClipboard == False:
        pass #TODO some error here


def transToText(t):
    """
    converts a translation tuple to unr text
    """
    return "Location=(X=%f,Y=%f,Z=%f)" % t

def rotToText(t):
    """
    converts a rotation tuple to unr text
    note: order of rotation in unr is y,z,x?
    """
    return "Rotation=(Pitch=%f,Yaw=%f,Roll=%f)" % t

def scaleToText(t):
    """
    converts a scaling tuple to unr text
    """
    return "DrawScale3D=(X=%f,Y=%f,Z=%f)" % t

    
def buildMeshText(meshSig, t=(0,0,0), r=(0,0,0), s=(1,1,1)):
    raw =""" 
Begin Map
   Begin Level
      Begin Actor Class=StaticMeshActor Name=StaticMeshActor_13 Archetype=StaticMeshActor'Engine.Default__StaticMeshActor'
         Begin Object Class=StaticMeshComponent Name=StaticMeshComponent0 ObjName=StaticMeshComponent_0 Archetype=StaticMeshComponent'Engine.Default__StaticMeshActor:StaticMeshComponent0'
            StaticMesh=StaticMesh'GP_Onslaught.Mesh.S_GP_Ons_Weapon_Locker'
         End Object
         StaticMeshComponent=StaticMeshComponent'StaticMeshComponent_0'
         Components(0)=StaticMeshComponent'StaticMeshComponent_0'
         %(translate)s
         %(rotate)s
         %(scale)s
         CollisionComponent=StaticMeshComponent'StaticMeshComponent_0'
      End Actor
   End Level
Begin Surface
End Surface
End Map"""
    mesh = raw % {"translate":transToText(t),
                  "rotate":rotToText(r),
                  "scale":scaleToText(s)}
    return mesh

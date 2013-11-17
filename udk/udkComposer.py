"""
the other main module to do operations with UnrealText.

This is the counterpart to :mod:`udkParser`.
The main task here is to convert ObjectInfo representations into UnrealText
ready for pasting into the Editor.

"""

from m2u.helper.ObjectInfo import ObjectInfo

def unrTextFromObjects(objInfoList):
    """ create UnrealText from the provided list of ObjectInfos
    """
    text = "Begin Map\n Begin Level\n"
    for obj in objInfoList:
        text += (unrTextFromOject(obj)+"\n")
    text += "End Level\n End Map\n"
    return text


def unrTextFromOject(objInfo):
    """ create UnrealText from the ObjectInfo
    
    Resulting text will begin with `Begin Actor` and end with `End Actor`.
    """
    # the header
    text = "Begin Actor "
    text += "Class=StaticMeshActor "
    text += "Name=" + objInfo.name + " "
    text += "Archetype=StaticMeshActor'Engine.Default__StaticMeshActor'"
    text += "\n"
    # the transform info
    text += transToText(objInfo.position) + "\n"
    text += rotToText(objInfo.rotation) + "\n"
    text += scaleToText(objInfo.scale) + "\n"
    # the rest
    text += objInfo.attrs["textblock"]
    # the footer
    text += "\nEnd Actor"
    return text


def transToText(t):
    """ converts a translation tuple to unr text """
    return "Location=(X=%f,Y=%f,Z=%f)" % t

def rotToText(t):
    """ converts a rotation tuple to unr text """
    return "Rotation=(Pitch=%f,Yaw=%f,Roll=%f)" % t

def scaleToText(t):
    """ converts a scaling tuple to unr text """
    return "DrawScale3D=(X=%f,Y=%f,Z=%f)" % t


"""The type of an object, `Class` in UnrealText must be 'interpreted' when
interacting with objects.

We differentiate in internal and common types. The internal type is the actual
classname as found in UnrealText, the common type is the one we use throughout
the m2u scripts and in the Program for reference.

For example: A 'StaticMeshActor' from Udk will be resembled by a 'Mesh'
object in the Program while a 'Mesh' in the Program will by default create
a 'StaticMeshActor' when being sent to Udk.

.. note: converting common type to internal type should only be
necessary for newly created objects that are not based on already
existing ones.

That means, when we duplicate an object that is present in UDK, we will get
the actual internal type from that directly, the common type will most likely
be ignored completely. But when a new Object is created in the Program and sent
to UDK, the translator needs to know what kind of object to create in UDK.

"""

internalTypeToCommonType={
    "StaticMeshActor":"Mesh",
    "InterpActor":"Mesh",
    "KActor":"Mesh",
    "Brush":"Mesh",
    
    "PointLight":"PointLight",
    "PointLightMoveable":"PointLight",
    "PointLightToggleable":"PointLight",
    "DominantPointLight":"PointLight",

    "DirectionalLight":"DirectionalLight",
    "DirectionalLightToggleable":"DirectionalLight",
    "DominantDirectionalLight":"DirectionalLight",
    "DominantDirectionalLightMoveable":"DirectionalLight",

    "SpotLight":"SpotLight",
    "SpotLightMoveable":"SpotLight",
    "SpotLightToggleable":"SpotLight",
    "DominantSpotLight":"SpotLight"
    }

def getCommonTypeFromInternal(t):
    """ return the matching common type for provided internal type
    
    if no type is found, return 'undefined',
    further processing of nodes of undefined commonType should be
    considered carefully
    """
    try:
        ct = internalTypeToCommonType[t]
        return ct
    except KeyError:
        return "undefined"

def getInternalTypeFromCommon(t):
    """ return the first matching internal type for provided common type
    """
    for it,ct in internalTypeToCommonType.items():
        if ct == t:
            return it
    print "Warning, no internal type found for "+t
    return None
"""
This is the main module to do operations with UnrealText. The main task here is to convert a copied UnrealText into representations for all of the contained objects and the reverse, creating UnrealText from those objects.


The average UrealText is constructed in the following manner:

Begin Map
    Begin Level
        Begin Actor
            ...
            Begin Object
                ...
            End Object
            ...
            Location =
            ...
        End Actor
    End Level
End Map


where there may be multiple Actors in each Level and each Actor may have multiple sub Object components.

The part we are most interested in are the Actors. We have one function to strip away the Map and Level parts and send every Actor block to a function which will create an ObjectInfo of that Actor. All the returned Infos will create a list of Actors of that Level and be returned from the parseMap function

"""


def parseActors(unrtext):
    """ This function will parse UnrealText beginning with Begin Map, ending with End Map or Level, and return a list of ObjectInfos of the Actors in the Level
    """
    pass

def _parseActor(unrtext):
    """ This function will parse UnrealText of a single Actor into an ObjectInfo representation.
    """
    pass

def unrTextFromObjects(objInfoList):
    """ This function will create UnrealText from the provided list of ObjectInfos
    """
    pass

def _unrTextFromOject(objInfo):
    pass
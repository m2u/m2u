"""
the main module to do operations with UnrealText.

The main task here is to convert a copied UnrealText into representations
for all of the contained objects and the reverse, creating UnrealText from
those objects. For the other way around, see :mod:`udkComposer`


The average UrealText is constructed in the following manner::

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

there may be multiple Actors in each Level and each Actor may have multiple
sub Object components.

The part we are most interested in are the Actors. We have one function to
strip away the Map and Level parts and send every Actor block to a function
which will create an ObjectInfo of that Actor. All the returned Infos will
create a list of Actors of that Level and be returned.


Why do we parse into ObjectInfos only to translate back into text when sending
stuff back to UDK, wouldn't it be faster if we simply did in-text replacement?
It might be faster in some instances where only short snippets in the text are
replaced. But i guess if you would for example extract the static-mesh
signature from an actor, the underlying regexp would have to search through
the whole string anyway. Why only get one information if you could get all
the information without much of an overhead?

But the main argument is, that it makes the implementation independent
from the used program and editor combination, we have only one place to look at
if something for the parsing process changes. And it is much easier to work with
objects in all the other functions than to fiddle with text-parsing everywhere.

"""

#TODO: what about differentiating objects like meshes and lights?
# maybe a commonobjType and a internalObjectType or so

import re

from m2u.helper.ObjectInfo import ObjectInfo

def parseActors(unrtext):
    """ parse UnrealText and return a list of ObjectInfos of the Actors in
    the Level.

    :param unrtext: the unreal text for the level
    :return: list of :class:`m2u.helper.ObjectInfo.ObjectInfo`

    Use this function to convert a complete level or multi-selection. 
    """
    objList = list()

    sindex = 0
    while True:
        sindex = unrtext.find("Begin Actor", sindex)
        if sindex == -1:
            break
        eindex = unrtext.find("End Actor", sindex) 
        actorText = unrtext[sindex:eindex]
        obj = parseActor(actorText, True)
        objList.append(obj)
    return objList
    

def parseActor(unrtext, safe=False):
    """ parse UnrealText of a single Actor into an ObjectInfo representation.

    :param unrtext: the unreal text for the level
    :param safe: the first line in unrtext is the Begin Actor line
    and the End Actor line is not present
    
    :return: instance of :class:`m2u.helper.ObjectInfo.ObjectInfo`

    .. note: if you provide text with more than one Actor in it, only the first
    Actor will be converted.
    If you have a multi-selection, use :func:`parseActors`
    
    """
    # to keep it simple we currently only get the entries we are interested
    # in and pile everything else up to a text, so we do no sub-object parsing
    # this may change in the future!
    
    sindex = 0
    # split every line and erase leading whitespaces, removes empty lines
    lines = re.split("\n+\s*", unrtext)
    # find the first line that begins the Actor (most likely the first line)
    if not safe: # no preprocessing was done, most likely the third line then
        for i in range(len(lines)):
            if lines[i].startswith("Begin Actor"):
                sindex = i
                break
    g = re.search("Name=(.+)\s+", lines[sindex])
    if not g: # no name? invalid text, obviously
        print "no name found for object"
        return None
    objname = g.group(1)
    objInfo = ObjectInfo(objname)
    textblock = ""
    for line in lines[sindex+1:]:
        # add jumping over sub-object groups (skip lines inbetween or so)
        # if line startswith "Begin Object"
        # dumb copy lines until
        # line startswith "End Object" is found
        # keep track of depth (begin obj,begin obj, end obj ->)
        if not safe and line.startswith("End Actor"):
            break # done reading actor
        elif line.startswith("Location="):
            objInfo.position = _getFloatTuple(line)
        elif line.startswith("Rotation="):
            objInfo.rotation = _getFloatTuple(line)
        elif line.startswith("DrawScale3D="):
            objInfo.scale = _getFloatTuple(line)
        else:
            textblock += ("\n"+line)
    objInfo.attrs["textblock"]=textblock
    return objInfo


float3Match = re.compile("=\(.+?=(.+?),.+?=(.+?),.+?=(.+?)\)")
def _getFloatTuple(text):
    """ get the float tuples from location, rotation etc. in unrtext """
    g = float3Match.search(text)
    a = [0.0, 0.0, 0.0] 
    for i in range(3):
        try:
            a[i] = float(g.group(i+1))
        except ValueError:
            pass
            # TODO: maybe do some information stuff here
    return (a[0],a[1],a[2])


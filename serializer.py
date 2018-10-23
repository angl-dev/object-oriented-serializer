try:
    from defusedexpat import pyexpat as expat
except ImportError:
    from xml.parsers import expat

from abc import ABCMeta, abstractproperty, abstractmethod
from collections import namedtuple
from enum import Enum

import lxml.etree as et

################################################################################
##                             Internal Constants                             ##
################################################################################
class _Constant(Enum):
    nodefault = 0
    recursive = 1

################################################################################
##                       Exposed Constants and Error Types                    ##
################################################################################
IGNORE = _Constant.nodefault        # ignore during serialization

class SerializableAttributeError(AttributeError):
    pass

class SerializableAPIError(RuntimeError):
    pass

class SerializableFormatError(ValueError):
    pass

################################################################################
##                    Helpers for attribute & child object                    ##
################################################################################
def _no_getter(self):
    raise AttributeError("Can't get property")

def _no_setter(self, value):
    raise AttributeError("Can't set property")

def _no_deleter(self):
    raise AttributeError("Can't delete property")

def _default_tuple(typename, *args, **kwargs):
    '''namedtuple with default values.'''
    kwkeys = kwargs.keys()
    T = namedtuple(typename, list(args) + kwkeys)
    T.__new__.__defaults__ = tuple([kwargs[k] for k in kwkeys])
    return T

class _Base(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __get__(self, obj, objtype=None):
        raise NotImplementedError

    @abstractmethod
    def __set__(self, obj, value):
        raise NotImplementedError

    @abstractmethod
    def __delete__(self, obj):
        raise NotImplementedError

    def __call__(self, fget):
        return self._replace(fget=fget, fset=self.fset or _no_setter, fdel=self.fdel or _no_deleter)

    def getter(self, fget):
        return self._replace(fget=fget, fset=self.fset or _no_setter, fdel=self.fdel or _no_deleter)

    def setter(self, fset):
        return self._replace(fget=self.fget or _no_getter, fset=fset, fdel=self.fdel or _no_deleter)

    def deleter(self, fdel):
        return self._replace(fget=self.fget or _no_getter, fset=self.fset or _no_setter, fdel=fdel)

################################################################################
##                   Attribute, child object & text content                   ##
################################################################################
class Attribute(_default_tuple("Attribute"
    ,required=False                 # if the attribute is required during serialization/deserialization
    ,default=_Constant.nodefault    # a default value if the attribute is not required
    ,key=None                       # the key of this attribute in the serialized format
    ,attr=None                      # the property name in the Python object
    ,fsrl=None                      # a function that serializes this value to a serializable data type
    ,fdsrl=None                     # a function that deserialize to other data types
    ,fget=None                      # property getter
    ,fset=None                      # property setter
    ,fdel=None                      # property deleter
    ), _Base):

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            if self.fget is not None:
                return self.fget(obj)
            else:
                return getattr(obj, '_Serializable__attr__' + self.key)
        except AttributeError:
            raise SerializableAttributeError("Can't get property: " + self.attr)

    def __set__(self, obj, value):
        try:
            if self.fset is not None:
                self.fset(obj, value)
            else:
                setattr(obj, '_Serializable__attr__' + self.key, value)
        except AttributeError:
            raise SerializableAttributeError("Can't set property: " + self.attr)

    def __delete__(self, obj):
        try:
            if self.fdel is not None:
                self.fdel(obj)
            else:
                delattr(obj, '_Serializable__attr__' + self.key)
        except AttributeError:
            raise SerializableAttributeError("Can't delete property: " + self.attr)

    def serializer(self, fsrl):
        return self._replace(fsrl=fsrl)

    def deserializer(self, fdsrl):
        return self._replace(fdsrl=fdsrl)

class ChildObject(_default_tuple("ChildObject"
    ,'factory'                      # factory function for creating a new child object
    ,required=False                 # if the child object(s) is(are) required
    ,multiple=False                 # if multiple child object(s) are accepted
    ,default=_Constant.nodefault    # a default value if the child object is not required
    ,key=None                       # the key of this child object(s) in the serialized format
    ,attr=None                      # the property name in the Python object
    ,fget=None                      # property getter
    ,fset=None                      # property setter
    ,fdel=None                      # property deleter
    ), _Base):

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            if self.fget is not None:
                return self.fget(obj)
            else:
                return getattr(obj, '_Serializable__child__' + self.key)
        except AttributeError:
            raise SerializableAttributeError("Can't get property: " + self.attr)


    def __set__(self, obj, value):
        try:
            if self.fset is not None:
                self.fset(obj, value)
            else:
                setattr(obj, '_Serializable__child__' + self.key, value)
        except AttributeError:
            raise SerializableAttributeError("Can't set property: " + self.attr)

    def __delete__(self, obj):
        try:
            if self.fdel is not None:
                self.fdel(obj)
            else:
                delattr(obj, '_Serializable__child__' + self.key)
        except AttributeError:
            raise SerializableAttributeError("Can't delete property: " + self.attr)

def RecursiveChildObject(required=False, multiple=False, default=_Constant.nodefault,
        key=None, attr=None, fget=None, fset=None, fdel=None):
    return ChildObject(_Constant.recursive, required=required, multiple=multiple, default=default,
            key=key, attr=attr, fget=fget, fset=fset, fdel=fdel)

class TextContent(_default_tuple("TextContent"
    ,required=False                 # if the text content is required during serialization/deserialization
    ,default=_Constant.nodefault    # a default value if the text content is not required
    ,attr=None                      # the property name in the Python object
    ,fsrl=None                      # a function that serializes this value to a serializable data type
    ,fdsrl=None                     # a function that deserialize to other data types
    ,fget=None                      # property getter
    ,fset=None                      # property setter
    ,fdel=None                      # property deleter
    ), _Base):

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            if self.fget is not None:
                return self.fget(obj)
            else:
                return getattr(obj, '_Serializable__textcontent__property')
        except AttributeError:
            raise SerializableAttributeError("Can't get property: " + self.attr)

    def __set__(self, obj, value):
        try:
            if self.fset is not None:
                self.fset(obj, value)
            else:
                setattr(obj, '_Serializable__textcontent__property', value)
        except AttributeError:
            raise SerializableAttributeError("Can't set property: " + self.attr)

    def __delete__(self, obj):
        try:
            if self.fdel is not None:
                self.fdel(obj)
            else:
                delattr(obj, '_Serializable__textcontent__property')
        except AttributeError:
            raise SerializableAttributeError("Can't delete property: " + self.attr)

    def serializer(self, fsrl):
        return self._replace(fsrl=fsrl)

    def deserializer(self, fdsrl):
        return self._replace(fdsrl=fdsrl)

################################################################################
##                           Serializable Meta-class                          ##
################################################################################
class _SerializableMeta(ABCMeta):
    def __new__(cls, name, bases, attrmap):
        # 0. let type works once to resolve inheritance
        T = super(_SerializableMeta, cls).__new__(cls, name, bases, attrmap)

        # 1. find all attributes, child objects and text contents
        attrs, children, text = {}, {}, None
        for k in dir(T):
            v = getattr(T, k)
            if isinstance(v, Attribute):
                v = v._replace(key=v.key or k, attr=k)
                if v.key in attrs:
                    conflict = attrs[v.key]
                    raise SerializableAPIError("Class {}: Two attributes have the same key: {} (property {} and {})"
                            .format(name, v.key, v.attr, conflict.attr))
                attrs[v.key] = v
                attrmap[k] = v
            elif isinstance(v, ChildObject):
                v = v._replace(key=v.key or k, attr=k)
                if v.key in children:
                    conflict = children[v.key]
                    raise SerializableAPIError("Class {}: Two child objects have the same key: {} (property {} and {})"
                            .format(name, v.key, v.attr, conflict.attr))
                children[v.key] = v
                attrmap[k] = v
            elif isinstance(v, TextContent):
                if text is not None:
                    raise SerializableAPIError("Class {}: Two or more text contents are defined (property {} and {})"
                            .format(name, k, text.attr))
                text = v._replace(attr=k)
                attrmap[k] = text

        # 2. check if text content and child objects are used at the same time
        if text is not None and len(children) > 0:
            raise SerializableAPIError("Class {}: Mixed usage of text content and child objects are not supported"
                    .format(name))

        # 3. update attrmap
        attrmap['_Serializable__attributes'] = attrs
        attrmap['_Serializable__children'] = children
        attrmap['_Serializable__textcontent'] = text.attr if text is not None else None

        # 4. redo type creation
        return super(_SerializableMeta, cls).__new__(cls, name, bases, attrmap)

################################################################################
##                           Serializable Base-class                          ##
################################################################################
class Serializable(object):

    __metaclass__ = _SerializableMeta

    # the following class variables will be overriden by _SerializableMeta 
    __attributes = None
    __children = None
    __textcontent = None

    def __init__(self, **kwargs):
        for attr in self.__attributes.itervalues():
            v = kwargs.pop(attr.attr, attr.default)
            if v is not _Constant.nodefault:
                setattr(self, attr.attr, v)
        for child in self.__children.itervalues():
            v = kwargs.pop(child.attr, child.default)
            if v is not _Constant.nodefault:
                setattr(self, child.attr, v)
        if self.__textcontent is not None:
            text = getattr(type(self), self.__textcontent)
            v = kwargs.pop(text.attr, text.default)
            if v is not _Constant.nodefault:
                setattr(self, text.attr, v)
        if kwargs:
            raise SerializableAPIError("Class {}: Unhandled key-value argument to __init__: {}"
                    .format(self.__class__.__name__, kwargs))

    @property
    def serialized_line(self):
        try:
            return self.__line
        except AttributeError:
            raise SerializableAttributeError("No line number available. Possible reasons are: "
                    "1) the object is not created via deserialization 2) line number is deleted by calling 'shrink'")

    @property
    def serialized_key(self):
        try:
            return self.__key
        except AttributeError:
            raise SerializableAttributeError("No key available. Possible reasons are: "
                    "1) the object is not created via deserialization 2) key is deleted by calling 'shrink'")

    def shrink(self):
        try:
            del self.__line
        except AttributeError:
            pass
        try:
            del self.__key
        except AttributeError:
            pass

    ############################################################################
    ##      Override these to customize serialization/deserialization         ##
    ############################################################################
    def deserialize_attribute(self, name, value, line=None):
        try:
            attr = self.__attributes[name]
        except KeyError:
            raise SerializableFormatError("Line {}: Object {} does not accept attribute {}"
                    .format(line or self.serialized_line, self.serialized_key, name))
        if attr.fdsrl is None:
            setattr(self, attr.attr, value)
        else:
            try:
                v = attr.fdsrl(value)
            except Exception as e:
                raise SerializableFormatError("Line {}: Failed to deserialize attribute {} (property {}): {} ({}: {})"
                    .format(line or self.serialized_line, name, attr.attr, value, e.__class__.__name__, e))
            setattr(self, attr.attr, v)

    def serialize_attribute(self, key):
        try:
            attr = self.__attributes[key]
        except KeyError:
            raise SerializableAPIError("Class {}: No serializable attribute {}"
                    .format(self.__class__.__name__, key))
        value = getattr(self, attr.attr, attr.default)
        if attr.required and value is _Constant.nodefault:
            raise SerializableAPIError("Class {}: Missing required serializable attribute {} (property {})"
                    .format(self.__class__.__name__, key, attr.attr))
        if attr.fsrl is None or value is _Constant.nodefault:
            return value
        try:
            return attr.fsrl(value)
        except Exception as e:
            raise SerializableAPIError("Class {}: Failed to serialize attribute {} (property {}): {} ({}: {})"
                    .format(self.__class__.__name__, key, attr.attr, value, e.__class__.__name__, e))

    def create_child_object(self, key, line):
        try:
            child = self.__children[key]
        except KeyError:
            raise SerializableFormatError("Line {}: Object {} does not accept child {}"
                    .format(line or self.serialized_line, self.serialized_key, key))
        try:
            obj = child.factory()
        except Exception as e:
            raise SerializableAPIError("Class {}: Failed to create child object {} (property {}) with given factory"
                    .format(self.__class__.__name__, key, child.attr))
        obj.__key = key
        obj.__line = line
        return obj

    def add_child_object(self, key, obj):
        try:
            child = self.__children[key]
        except KeyError:
            raise SerializableFormatError("Line {}: Object {} does not accept child {}"
                    .format(obj.serialized_line, self.serialized_key, key))
        if child.multiple:
            try:
                l = getattr(self, child.attr)
            except AttributeError:
                l = []
                setattr(self, child.attr, l)
            try:
                l.append(obj)
            except Exception as e:
                raise SerializableAPIError("Line {}: Failed to append child object {} (property {}) ({}: {})"
                        ,format(obj.serialized_line, key, child.attr, e.__class__.__name__, e))
        else:
            v = getattr(self, child.attr, child.default)
            if v is not child.default:
                raise SerializableFormatError("Line {}: Object {} only accepts one child {} (property {})"
                        .format(obj.serialized_line, self.serialized_key, key, child.attr))
            setattr(self, child.attr, obj)

    def ignore_child_object(self, key, obj):
        return False

    def deserialize_textcontent(self, value, line=None):
        if self.__textcontent is None:
            raise SerializableFormatError("Line {}: Object {} does not accept text content"
                    .format(line or self.serialized_line, self.serialized_key))
        text = getattr(type(self), self.__textcontent)
        if text.fdsrl is None:
            setattr(self, text.attr, value)
        else:
            try:
                v = text.fdsrl(value)
            except Exception as e:
                raise SerializableFormatError("Line {}: Failed to deserialize attribute {} (property {}): {} ({}: {})"
                    .format(line or self.serialized_line, name, text.attr, value, e.__class__.__name__, e))
            setattr(self, text.attr, v)

    def serialize_textcontent(self):
        if self.__textcontent is None:
            raise SerializableAPIError("Class {}: No serializable text content"
                    .format(self.__class__.__name__))
        text = getattr(type(self), self.__textcontent)
        value = getattr(self, text.attr, text.default)
        if text.required and value is _Constant.nodefault:
            raise SerializableAPIError("Class {}: Missing required text content"
                    .format(self.__class__.__name__))
        if text.fsrl is None or value is _Constant.nodefault:
            return value
        try:
            return text.fsrl(value)
        except Exception as e:
            raise SerializableAPIError("Class {}: Failed to serialize text content (property {}): {} ({}: {})"
                    .format(self.__class__.__name__, text.attr, value, e.__class__.__name__, e))

    def after_deserialize_attributes(self):
        for attr in self.__attributes.itervalues():
            if attr.required and not hasattr(self, attr.attr):
                raise SerializableFormatError("Line {}: Missing required attribute {} (property {})"
                        .format(self.serialized_line, attr.key, attr.attr))

    def after_deserialize_all(self):
        for child in self.__children.itervalues():
            if child.required and not hasattr(self, child.attr):
                raise SerializableFormatError("Line {}: Missing required child object {} (property {})"
                        .format(self.serialized_line, child.key, child.attr))
        if self.__textcontent is None:
            return
        text = getattr(type(self), self.__textcontent)
        if text.required and not hasattr(self, text.attr):
            raise SerializableFormatError("Line {}: Missing required text content (property {})"
                    .format(self.serialized_line, text.attr))

    ############################################################################
    ##                              Internal API                              ##
    ############################################################################
    def _dump_xml(self, xmlfile, tag, depth, pretty=False):
        attrs = dict( (key, value) for key in self.__attributes
                for value in (self.serialize_attribute(key), ) if value is not _Constant.nodefault )
        if pretty:
            xmlfile.write('\t' * depth)
        with xmlfile.element(tag, attrs):
            if self.__textcontent is not None:
                value = self.serialize_textcontent()
                if value is not _Constant.nodefault:
                    xmlfile.write(value)
            elemBody = False
            for key, child in self.__children.iteritems():
                try:
                    children = getattr(self, child.attr)
                except AttributeError:
                    if child.required:
                        raise SerializableAPIError("Class {}: Missing required child object {} (property {})"
                                .format(self.__class__.__name__, key, child.attr))
                    else:
                        continue
                if child.multiple:
                    try:
                        it = iter(children)
                    except TypeError:
                        raise SerializableAPIError("Class {}: Child object {} (property {}) is not iterable"
                                .format(self.__class__.__name__, key, child.attr))
                    hasChild = False
                    for obj in it:
                        hasChild = True
                        if not self.ignore_child_object(key, obj):
                            if pretty and not elemBody:
                                xmlfile.write('\n')
                                elemBody = True
                            obj._dump_xml(xmlfile, key, depth + 1, pretty)
                    if not hasChild:
                        raise SerializableAPIError("Class {}: Missing required child object {} (property {})"
                                .format(self.__class__.__name__, key, child.attr))
                else:
                    if not self.ignore_child_object(key, children):
                        if pretty and not elemBody:
                            xmlfile.write('\n')
                            elemBody = True
                        children._dump_xml(xmlfile, key, depth + 1, pretty)
            if pretty and elemBody:
                xmlfile.write('\t' * depth)
        if pretty and depth > 0:
            xmlfile.write('\n')

################################################################################
##                                 Exposed API                                ##
################################################################################
def serialize_xml(f, root_tag, obj, pretty=False, **kwargs):
    with et.xmlfile(f, **kwargs) as xf:
        obj._dump_xml(xf, root_tag, 0, pretty)

class _Parser(object):
    def __init__(self, root_tag, root_factory, **kwargs):
        self.encoding = kwargs.pop('encoding', None)
        if not callable(root_factory):
            raise SerializableAPIError("Factory not callable")
        self.root_tag = root_tag
        self.root_factory = root_factory
        self.root = None
        self.stack = []
        self.dcache = ''
        if self.encoding is None:
            self.parser = expat.ParserCreate()
        else:
            self.parser = expat.ParserCreate(self.encoding)
        self.parser.StartElementHandler = self.start_element_handler
        self.parser.EndElementHandler = self.end_element_handler
        self.parser.CharacterDataHandler = self.character_data_handler

    def start_element_handler(self, name, attributes):
        if self.encoding is not None:
            name = name.encode(self.encoding)
        obj = None
        if len(self.stack) == 0:
            # root
            if name != self.root_tag:
                raise ValueError("Line {}: Expecting tag {} ({} found)"
                        .format(self.parser.CurrentLineNumber, self.root_tag, name))
            try:
                obj = self.root_factory()
            except Exception as e:
                raise SerializableAPIError("Parser: Failed to create root object with given factory")
            obj._Serializable__line = self.parser.CurrentLineNumber
            obj._Serializable__key = self.root_tag
        else:
            parent = self.stack[-1]
            obj = parent.create_child_object(name, self.parser.CurrentLineNumber)
        for k, v in attributes.iteritems():
            if self.encoding is not None:
                k = k.encode(self.encoding)
                if isinstance(v, basestring):
                    v = v.encode(self.encoding)
            obj.deserialize_attribute(k, v, self.parser.CurrentLineNumber)
        obj.after_deserialize_attributes()
        self.stack.append(obj)
        self.dcache = ''

    def end_element_handler(self, name):
        obj = self.stack.pop()
        data = self.dcache.strip()
        if data:
            obj.deserialize_textcontent(data, self.parser.CurrentLineNumber)
        self.dcache = ''
        obj.after_deserialize_all()
        if len(self.stack) == 0:
            self.root = obj
        else:
            self.stack[-1].add_child_object(name, obj)

    def character_data_handler(self, data):
        if self.encoding is not None:
            data = data.encode(self.encoding)
        self.dcache += data

def deserialize_xml(f, root_tag, root_factory, **kwargs):
    parser = _Parser(root_tag, root_factory, **kwargs)
    parser.parser.ParseFile(f)
    return parser.root

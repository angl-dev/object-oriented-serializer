# Memory-efficient data serialization library

## Design goals 
1. Memory efficiency:
    * Low memory overhead for the objects
    * Generator-based serialization & deserialization
2. Serialization schema:
    * Define data schema with `class`es and `property`-like decorators
    * Use (multi-) inheritance to extend, modify and combine schemas
3. User interface:
    * Detailed error report for data that don't match the defined schema

## Vocabulary

To minimize possible confusions of the description below, we define the
following vocabulary:

* *serializable class*: a class inheriting the `Serializable` class
* *serializable object*: an instance of a serializable class
* *serializable property* a `Attribute`, `ChildObject` or `TextContent`
  property of a serializable class
* *key*: key in the serialized format, that is, tag in XML, key in JSON/YAML

## Basic usage

The key class is the `Serializable` class. Inherit this class to create a
schema for serializable objects. Use `Attribute`, `ChildObject` and
`TextContent` to add schema on the corresponding contents to this object.

A simple example:

```python
from serializer import *

class Animal(Serializable):
    type = Attribute(required=True)
    description = TextContent()

class Zoo(Serializable):
    animal = ChildObject(Animal, required=True, multiple=True)
```

Use `deserialize_xml` to deserialize a XML file with a serializable class
(`deserialize_json` and `deserialize_yaml` will be added later). This function
takes three arguments, the first being a file-like object to deserialize from,
the second being the root key, and the third being a factory function which
can create serializable objects (could be the serializable class itself).

```python
from StringIO import StringIO
zoo = deserialize_xml(StringIO('''
    <zoo>
        <animal type="cat">The cat, often referred to as the domestic cat to
        distinguish from other felids and felines, is a small, typically
        furry, carnivorous mammal.</animal>
        <animal type="dog">The domestic dog is a member of the genus Canis,
        which forms part of the wolf-like canids, and is the most widely
        abundant terrestrial carnivore.</animal>
    </zoo>
    '''), 'zoo', Zoo)
```

After deserialization, the serializable object `zoo` has everything stored in
it. All serializable properties can be accessed just like normal properties.

```python
for animal in zoo.animal:
    print animal.type
# output
# > cat
# > dog
```

In addition to deserializing from a file, serializable objects can also be
created and modified in the Python program.

```python
cow = Animal(type='cow')
cow.description=("Cattle-colloquially cows-are the most common type of large "
    "domesticated ungulates.")
zoo.animal.append(cow)
```

[_Pitfalls_: uninitialized properties](#uninitialized-properties)

Finally, use `serialize_xml` to serialize to a XML file (`serialze_json` and
`serialize_yaml` will be added later). This function also takes three
arguments, the first being a file-like object to deserialize to , the second
being the root key, and the third being a serializable object. An optional
argument is `pretty`, which enables pretty printing, and is set to `False` by
default.

```python
outstream = StringIO()
serialize_xml(outstream, 'zoo', zoo, pretty=True)
print outstream.getvalue()
# output
# > <zoo>
# >     <animal type="cat">The cat, often referred to as the domestic cat to
# >     distinguish from other felids and felines, is a small, typically
# >     furry, carnivorous mammal.</animal>
# >     <animal type="dog">The domestic dog is a member of the genus Canis,
# >     which forms part of the wolf-like canids, and is the most widely
# >     abundant terrestrial carnivore.</animal>
# >     <animal type="cow">Cattle-colloquially cows-are the most common type
# >     of large domesticated ungulates.</animal>
# > </zoo>
```

## Advanced usage I: Combine schemas

## Pitfalls

### Uninitialized Properties

A `Attribute`, `ChildObject`, and `TextContent` property are uninitialized when
a serializable object is created, unless:
1. a `default` value is set when defining the property
2. the property is set with argument passed to `__init__`
3. the property is deserialized from a file

If a property is uninitialized, accessing it will raise a
`SerializableAttributeError`. To avoid complex logic checking if a
serializable property is initialized, always define `default` value, or set it
in the inherited `__init__`.

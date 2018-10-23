from serializer import *

class Animal(Serializable):
    type = Attribute(required=True)
    description = TextContent()

class Zoo(Serializable):
    animal = ChildObject(Animal, required=True, multiple=True)

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

for animal in zoo.animal:
    print animal.type

cow = Animal(type='cow')
cow.description=("Cattle-colloquially cows-are the most common type of large "
    "domesticated ungulates.")
zoo.animal.append(cow)

outstream = StringIO()
serialize_xml(outstream, 'zoo', zoo, pretty=True)
print outstream.getvalue()

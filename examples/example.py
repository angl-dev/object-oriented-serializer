from serializer import *

## Basic usage

class Animal(Serializable):
    type = SerializableAttribute(required=True)
    description = SerializableTextContent()

class Zoo(Serializable):
    animal = SerializableChildObject(Animal, required=True, multiple=True)

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

## Advanced usage I

class AnimalCategory(Animal):
    @property
    def description(self):  # remove the text content from the schema
        raise NotImplementedError

    subtype = SerializableChildObject(Animal, required=True, multiple=True)

class BetterZoo(Zoo):
    category = SerializableChildObject(AnimalCategory, required=True, multiple=True)

zoo2 = deserialize_xml(StringIO('<zoo><category type="mammal">'
    '<subtype type="human">Humans (taxonomically, Homo sapiens) are the only '
    'extant members of the subtribe Hominina.</subtype>'
    '<subtype type="whale">Whales are a widely distributed and diverse group '
    'of fully aquatic placental marine mammals.</subtype>'
    '</category><animal type="fish">Fish are gill-bearing aquatic craniate '
    'animals that lack limbs with digits.</animal></zoo>'),
    'zoo', BetterZoo)

for category in zoo2.category:
    for subtype in category.subtype:
        print subtype.type
for animal in zoo2.animal:
    print animal.type

class DetailedAnimal(Animal):
    features = SerializableAttribute(required=False, key='feature')

    @features.deserializer
    def features(s):
        return s.split()

    @features.serializer
    def features(v):
        return ' '.join(v)

animal = deserialize_xml(StringIO('<animal type="bird" feature="fly sing">'
    'Birds, also known as Aves, are a group of endothermic vertebrates, '
    'characterised by feathers, toothless beaked jaws, the laying of '
    'hard-shelled eggs, a high metabolic rate, a four-chambered heart, and a '
    'strong yet lightweight skeleton.</animal>'), 'animal', DetailedAnimal)
for feature in animal.features:
    print feature

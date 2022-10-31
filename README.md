# soda - a fast SVG generation tool

Here's some basic usage:

```python
from soda import Tag, Root

# root is a custom svg tag
root = Root(viewBox="0 0 10 10")(
    Tag.rect(width=10, height=10, fill="#ff5"),
    Tag.circle(cx=5, cy=5, r=4, fill="#222")
)

print(root.render(pretty=True))
```

## Installation

Just use `python setup.py` or `python -m pip install soda-svg`

## Tag construction

The main class of the module is `Tag`. You can create it with a constructor:

```python
Tag("g")
```

or with a shorthand:

```python
Tag.g
```

You can also pass children and attributes into the constructor:

```python
Tag("g", child1, child2, attr1=1, attr2=2)
```

or as call arguments (this would change tag in place, no additional copies):

```python
Tag("g")(child1, attr1=1)(child2, child3, attr2=10, attr3=3)
# or
Tag.g(child1, attr1=1)(child2, child3, attr2=10, attr3=3)

# '_' to '-' conversion
Tag.g(child1, attr_1=1)(child2, child3, attr_2=10, attr_3=3) # <g attr-1="1" attr-2="10" attr-3="3" >child1child2child3</g>
```

## Float rounding

As floats can be used as attribute values (even though in resulting SVG every value is a string), module will round floats to 3 digits after the decimal point:

```python
from soda import Tag

g = Tag.g(x=1/3)
print(g.render()) # '<g x="0.333"/>'

```

To change this behaviour, edit `soda.config.decimal_length` before value is assigned:

```python
from soda import Tag, config as soda_config

soda_config.decimal_length = 4

g = Tag.g(x=1/3)
print(g.render()) # '<g x="0.3333"/>'

soda_config.decimal_length = 2
g(y=1/3)

print(g.render()) # '<g x="0.3333" y="0.33"/>'

```

## Attribute conversion

For convenience, leading and trailing underscores are removed by default, and underscores in the middle of words are replaced with hyphens:

```python
from soda import Tag

g = Tag.g(cla_ss_="test") 

print(g.render()) # <g cla-ss="test"/>

```

To disable replacing behavior, use `config` class:

```python
from soda import Tag, config as soda_config

soda_config.replace_underscores = False

g = Tag.g(cla_ss_="test") 

print(g.render()) # <g cla_ss="test"/>

```

...and to disable stripping of leading/traililng underscores:

```python
from soda import Tag, config as soda_config

soda_config.strip_underscores = False

g = Tag.g(cla_ss_="test") 

print(g.render()) # <g cla-ss="test"/>
```

It's important to do that before tag creation, as all conversions are happening at the tag creation time:

```python

from soda import Tag, config as soda_config

g1 = Tag.g(cla_ss_="test") # g.attributes == {"cla-ss": "test"}

soda_config.replace_underscores = False

g2 = Tag.g(cla_ss_="test") # g.attributes == {"cla_ss_": "test"}

print(g1.render()) # <g cla-ss="test"/>
print(g2.render()) # <g cla_ss_="test"/>

```

## Creating a Tag from XML string

*new in 1.1.0*

You can use `Tag.from_str(xml_string)` to parse an XML document in that string.    
Note that currently this doesn't preserve any comments or declarations of original document.

```python
from soda import Tag, Root

root = Root(viewBox="0 0 10 10")(
    Tag.rect(width=10, height=10, fill="#ff5"),
    Tag.circle(cx=5, cy=5, r=4, fill="#222")
)

rendered_root = root.render(pretty=True)
new_root = Tag.from_str(rendered_root)

assert rendered_root == new_root.render(pretty=True)
```

### Text

Basic text handling is pretty straightforward:

```python
from soda import Tag

Tag.text("Hello, World") # just pass a string as a children
```

This code is roughly equivalent to:

```python
from soda import Tag, Literal

Tag.text(Literal("Hello, World"))
```

...except that first piece doesn't create a `Literal` object.

If you need to add unescaped text (such as prerendered XML), you should pass `escape=False` to a `Literal` constructor:

```python
from soda import Tag, Literal

Tag.g(Literal('<path d="M0 0 L10 0 Z"/>', escape=False))
```

## Accessing data

`tag[attr]` syntax can be used to manage tag attributes (where `attr` should be a string).

```python
from soda import Tag

tag = Tag.g
tag["id"] = "yes-thats-an-id" # sets attribute
tag["cool"] = None # deletes attribute if exists, otherwise does nothing
print(tag["id"]) # prints attribute
print(tag["non-existent-attribute"]) # prints None
```

`tag[index]` syntax can be used to manage tag children (where `index` should be either integer or slice).

```python
from soda import Tag

tag = Tag.g(Tag.a)
tag[0]["href"] = "https://github.com/evtn/soda"
print(tag[1]) # IndexError
print(tag[0]) # prints <a href="https://github.com/evtn/soda" />
```

Children can also be accessed directly through `tag.children` attribute.

## Fragments

Fragments use concept similar to React's fragment. It renders just it's children:

```python
from soda import Tag, Fragment

tag = Tag.g(
    Fragment(Tag.a, Tag.a)
)
print(tag) # <g><a/><a/></g>

```

## Paths

_new in 0.1.7_

There is a builder for SVG path commands in soda:

<svg viewBox="0 0 100 100">
    <rect width="100%" height="100%" fill="white"/>
    <path d="M 10,30
           A 20,20 0,0,1 50,30
           A 20,20 0,0,1 90,30
           Q 90,60 50,90
           Q 10,60 10,30 z"
    />
</svg>

You can build a list of path commands using descriptive command names:

```python
from soda import Tag, Root, Path

commands = (
    Path.moveto(x=10, y=30),
    Path.arc(
        radius_x=20,
        radius_y=20,
        # for convenience, omitted arguments
        # (here: x_axis_rotation and large_arc_flag) are set to 0
        sweep_flag=1,
        x=50,
        y=30,
    ),
    Path.arc(
        radius_x=20,
        radius_y=20,
        sweep_flag=1,
        x=90,
        y=30,
    ),
    Path.quadratic(
        x1=90,
        y1=60,
        x=50,
        y=90,
    ),
    Path.quadratic(
        x1=10,
        y1=60,
        x=10,
        y=30,
    ),
    Path.close()
)


```

...or using common SVG command names (letter case signifies if command is relative):

```python

# or

commands = (
    Path.M(10, 30),
    Path.A(20, 20, 0, 0, 1, 50, 30),
    Path.A(20, 20, 0, 0, 1, 50, 30),
    Path.Q(90, 60, 50, 90),
    Path.Q(10, 60, 10, 30),
    Path.Z()
)

```

...and render it with `Path.build(*commands, compact=False)` method

```python

root = Root(
    viewBox="0 0 100 100",
    use_namespace=True,
)(
    Tag.rect(width="100%", height="100%", fill="white"),
    Tag.path()(
        d=Path.build(*commands)
    )
)

print(root.render(pretty=True))

"""
yields:

<svg
  viewBox="0 0 100 100"
  version="2.0"
  xmlns="http://www.w3.org/2000/svg"
  xmlns:xlink="http://www.w3.org/1999/xlink"
>
  <rect
    width="100%"
    height="100%"
    fill="white"
  />
  <path
    d="M 10 30 A 20 20 0 0 1 50 30 A 20 20 0 0 1 50 30 Q 90 60 50 90 Q 10 60 10 30 Z"
  />
</svg>
"""
```

You can also optimize resulting path with `compact` argument:

```python
print(Path.build(*commands, compact=True))
# prints M10 30A20 20 0 0 1 50 30A20 20 0 0 1 50 30Q90 60 50 90Q10 60 10 30Z
```

## Points

_new in 1.0.3_

To work with coordinates, you can use `Point` class:

```python
from soda import Point

a = Point(1, 2)
b = Point(4, 5)
```

In any context where a point could be used, "point-like" values can be used:

-   `(1, 2)` <-> `Point(1, 2)`
-   `[1, 2]` <-> `Point(1, 2)`
-   `1` <-> `Point(1, 1)`

You can use coordinates of a point:

```python
print(a) # Point[1, 2]
print(a.x) # 1
print(a.coords) # (1, 2)
print([*a]) # [1, 2] (same as [*a.coords])
```

...perform mathematical operations on points:

```python
print(a + b) # Point[5, 7]
print(a - b) # Point[-3, -3]
print(a * b) # Point[4, 10] (a.x * b.x, a.y * b.y)
print(a / b) # Point[0.25, 0.4]
print(a % b) # Point[1, 2]
```

...and any point-like values:

```python
print(a + 10) # Point[11, 12]
print(a * 2) # Point[2, 4]
```

You also can calculate distance between points and rotate a point around some point:

```python
from math import pi

print(a.distance(b)) # 4.242640687119285
print(a.distance()) # 2.23606797749979 (distance between a and (0, 0), basically the length of a vector)
print(a.rotate(degrees=90)) # Point[-2, 1]
print(a.rotate((10, 10), degrees=90))
print(a.rotate((10, 10), radians=pi / 2)) # Point[18, 1]
```

...and get a normalized vector:

```python
print(a.normalized()) # Point[0.4472135954999579, 0.8944271909999159]
```

You also can get an angle (in radians) between two vectors (with specified starting point):

```python
print(a.angle(b)) # 0.21109333322274684
print(a.angle(b, (10, 10))) # 0.03190406448501816 (second argument specifies starting point (0, 0) by default)
print(a.angle()) # 1.1071487177940904 (angle between `a` and (1, 0) vector)

print(
    a.angle(
        a.rotate(radians=2)
    )
) # 2
```

### Converting angles

To convert between radians and degrees, use `radians_to_degrees` and `degrees_to_radians`:

```python
from soda.point import radians_to_degrees, degrees_to_radians
from math import pi

print(degrees_to_radians(90) / pi) # 0.5
print(radians_to_degrees(degrees_to_radians(90))) # 90
```

### Using as attributes

`Point.as_` provides a convenient way of using points as tag attributes:

```python
from soda import Tag, Point

size = Point(100, 200)

print(size.as_()) # {"x": 100, "y": 200}
print(size.as_("width", "height")) # {"width": 100, "height": 200}


print(
    Tag.rect(
        **size.as_("width", "height")
    )
) # <rect width="100" height="200"/>

```

### PointPath

A version of [`Path`](#paths) accepting `Point` instead of some arguments.
Where Path.something(...) accepts coordinates (as two arguments) or some size (like `radius_x` and `radius_y` in `arc`), `PointPath` accepts a point-like object instead.

## Custom components

You can build custom components, using different approaches:

### Building a tree on init

Builds a tree on every component creation

```python
from soda import Tag, Fragment

class CustomComponent(Fragment):
    def __init__(self):
        children = Tag.g(
            Tag.anythingother,
            Tag.lalala(
                Tag.yes,
                Tag.no
            )
        )
        super().__init__(*children)

CustomComponent().render()
```

### Functional approach

Builds a tree on every call

```python
from soda import Tag

def custom_component():
    return Tag.g(
        Tag.anythingother,
        Tag.lalala(
            Tag.yes,
            Tag.no
        )
    )

custom_component().render()
```

## Speed

soda is able to render tens of thousands tags per second, but if you wanna optimize your execution, there are some tips:

### Building a tree efficiently

If you using the same structure many times (especially if it's a heavy one), avoid rebuilds. Rather than building a new tree every time, consider changing specific parts of it when needed. It won't speed up the render time, though

### Prerendering

If you have some static tags, you can use `tag.prerender()` to get a prerendered `Literal`.
This could speed up your render significantly in some cases.

### Pretty or not?

Pretty render gives a nice formatted output, which is very readable.  
~~But using `pretty=True` in rendering would make renders 3-5x slower than default `pretty=False`.~~  
Starting with 0.1.5 version, pretty rendering is roughly the same in speed as default one.

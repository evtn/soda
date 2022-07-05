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
Also, you can just edit `tag.attributes` directly (which is a bad idea, actually, don't do that)

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

...or using common SVG command names:

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

...and render it with `Path.build(*commands, sep=", ", compact=False)` method

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
    d="M 10 30, A 20 20 0 0 1 50 30, A 20 20 0 0 1 50 30, Q 90 60 50 90, Q 10 60 10 30, Z"
  />
</svg>
"""
```

You can also replace command separator (`sep` argument to build), or optimize resulting path with `compact` argument (overrides `sep`):

```python
print(Path.build(*commands, sep=" "))
# prints 'M 10 30 A 20 20 0 0 1 50 30 A 20 20 0 0 1 90 30 Q 90 60 50 90 Q 10 60 10 30 Z'

print(Path.build(*commands, compact=True))
# prints M10 30A20 20 0 0 1 50 30A20 20 0 0 1 50 30Q90 60 50 90Q10 60 10 30Z
```

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

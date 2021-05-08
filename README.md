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

## Custom components

You can build custom components, using different approaches:

### Custom render

The most straightforward one, builds a tree on every render:

```python
from soda import Tag, Fragment

class CustomComponent(Fragment):
    def render(self, pretty: bool = False) -> str:
        return Tag.g(
            Tag.anythingother,
            Tag.lalala(
                Tag.yes,
                Tag.no
            )
        ).render(pretty)

CustomComponent().render()
```

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

### Building a tree efficiently

If you using the same structure many times (especially if it's a heavy one), avoid rebuilds. Rather than building a new tree every time, consider changing specific parts of it when needed. It won't speed up the render time, though

### Prerendering

If you have some static tags, you can use `tag.prerender()` to get a prerendered `Literal`.
This could speed up your render significantly in some cases.

### Pretty or not?

Pretty render gives a nice formatted output, which is very readable.
But using `pretty=True` in rendering would make renders 3-5x slower than default `pretty=False`.

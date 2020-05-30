`# Pervane

![](https://github.com/hakanu/pervane/raw/master/docs/pervane_logo_small.png)

Table of Contents

[TOC]

# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6
# Heading 1 link [Heading link](https://github.com/hakanu/pervane "Heading link")
## Heading 2 link [Heading link](https://github.com/hakanu/pervane "Heading link")
### Heading 3 link [Heading link](https://github.com/hakanu/pervane "Heading link")
#### Heading 4 link [Heading link](https://github.com/hakanu/pervane "Heading link")
##### Heading 5 link [Heading link](https://github.com/hakanu/pervane "Heading link")
###### Heading 6 link [Heading link](https://github.com/hakanu/pervane "Heading link")

#### Heading (underline)

This is an H1
=============

This is an H2
-------------
----

Hello
### Blockquotes

> Blockquotes

Blockquotes

> With the link [link](https://github.com/hakanu/pervane)。

### Links

[link](https://github.com/hakanu/pervane)

[link](https://github.com/hakanu/pervane, "yolo")

Direct link：<https://github.com/hakanu/pervane>

[anchor-id]: http://www.this-anchor-link.com/

[mailto:test.test@gmail.com](mailto:test.test@gmail.com)

#### Inline code

`pip install pervane`

#### Table

    | First Header  | Second Header |
    | ------------- | ------------- |
    | Content Cell  | Content Cell  |
    | Content Cell  | Content Cell  |

#### JS

```javascript
function test() {
  console.log("Hello world!");
}
```

#### HTML

```html
<!DOCTYPE html>
<html>
    <head>
        <mate charest="utf-8" />
        <meta name="keywords" content="Editor.md, Markdown, Editor" />
        <title>Hello world!</title>
        <style type="text/css">
            body { color:#444;font-family: Arial;background:#fff; }
            ul { list-style: none;}
            img { border:none;vertical-align: middle; }
        </style>
    </head>
    <body>
        <h1 class="text-xxl">Hello world!</h1>
        <p class="text-green">Plain text</p>
    </body>
</html>
```

### Images

Image:

![](https://images.unsplash.com/photo-1578241561880-0a1d5db3cb8a?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80)

> Follow your heart.

![](https://images.unsplash.com/photo-1578165219176-ece04edbd053?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80)

#### (Image + Link)：

[![](https://images.unsplash.com/photo-1577998076239-ea6d9a7dcd82?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1050&q=80)](https://github.com/hakanu/pervane)

### Lists

#### Unordered Lists (-)

- One
- Two
- Three

#### Unordered Lists (*)

* One
* Two
* Three

#### Unordered Lists (+)

+ One
+ Two
    + One-1
    + Two-2
    + Three-3
+ Three
    * One
    * Two
    * Three

#### Ordered Lists (-)

1. One
2. Two
3. Three

#### GFM task list

- [x] GFM task list 1
- [x] GFM task list 2
- [ ] GFM task list 3
    - [ ] GFM task list 3-1
    - [ ] GFM task list 3-2
    - [ ] GFM task list 3-3
- [ ] GFM task list 4
    - [ ] GFM task list 4-1
    - [ ] GFM task list 4-2

----

### Tables

| Text       | Price   |  Amount  |
| --------   | -----:  | :----:  |
| Cell      | $1600   |   5     |
| Cell        |   $12   |   12   |
| Cell       |    $1    |  234  |

First Header  | Second Header
------------- | -------------
Content Cell  | Content Cell
Content Cell  | Content Cell 

| First Header  | Second Header |
| ------------- | ------------- |
| Content Cell  | Content Cell  |
| Content Cell  | Content Cell  |

| Function name | Description                    |
| ------------- | ------------------------------ |
| `help()`      | Display the help window.       |
| `destroy()`   | **Destroy your computer!**     |

| Left-Aligned  | Center Aligned  | Right Aligned |
| :------------ |:---------------:| -----:|
| col 3 is      | some wordy text | $1600 |
| col 2 is      | centered        |   $12 |
| zebra stripes | are neat        |    $1 |

| Item      | Value |
| --------- | -----:|
| Computer  | $1600 |
| Phone     |   $12 |
| Pipe      |    $1 |

----

#### HTML Entities Codes

&copy; &  &uml; &trade; &iexcl; &pound;
&amp; &lt; &gt; &yen; &euro; &reg; &plusmn; &para; &sect; &brvbar; &macr; &laquo; &middot;

X&sup2; Y&sup3; &frac34; &frac14;  &times;  &divide;   &raquo;

18&ordm;C  &quot;  &apos;

[========]

### Emoji :smiley:

> Blockquotes :star:

#### GFM task lists & Emoji & fontAwesome icon emoji & editormd logo emoji :editormd-logo-5x:

- [x] :smiley: @mentions, :smiley: #refs, [links](), **formatting**, and <del>tags</del> supported :editormd-logo:;
- [x] list syntax required (any unordered or ordered list supported) :editormd-logo-3x:;
- [x] [ ] :smiley: this is a complete item :smiley:;
- [ ] []this is an incomplete item [test link](#) :fa-star: @pandao; 
- [ ] [ ]this is an incomplete item :fa-star: :fa-gear:;
    - [ ] :smiley: this is an incomplete item [test link](#) :fa-star: :fa-gear:;
    - [ ] :smiley: this is  :fa-star: :fa-gear: an incomplete item [test link](#);
 
#### Escape

\*literal asterisks\*

[========]
            
### TeX(KaTeX) - math formulas

$$E=mc^2$$

行内的公式$$E=mc^2$$行内的公式，行内的$$E=mc^2$$公式。

$$x > y$$

$$\(\sqrt{3x-1}+(1+x)^2\)$$

$$\sin(\alpha)^{\theta}=\sum_{i=0}^{n}(x^i + \cos(f))$$

```math
\displaystyle
\left( \sum\_{k=1}^n a\_k b\_k \right)^2
\leq
\left( \sum\_{k=1}^n a\_k^2 \right)
\left( \sum\_{k=1}^n b\_k^2 \right)
```

```katex
\displaystyle 
    \frac{1}{
        \Bigl(\sqrt{\phi \sqrt{5}}-\phi\Bigr) e^{
        \frac25 \pi}} = 1+\frac{e^{-2\pi}} {1+\frac{e^{-4\pi}} {
        1+\frac{e^{-6\pi}}
        {1+\frac{e^{-8\pi}}
         {1+\cdots} }
        } 
    }
```

```latex
f(x) = \int_{-\infty}^\infty
    \hat f(\xi)\,e^{2 \pi i \xi x}
    \,d\xi
```

### Page break

> Print Test: Ctrl + P

[========]

### Flowchart

```flow
st=>start: start the process
op=>operation: Pull records from db
cond=>condition: User exists Yes or No?
e=>end: stop

st->op->cond
cond(yes)->e
cond(no)->op
```

[========]
                    
### 绘制序列图 Sequence Diagram
                    
```seq
Bob->Lucy: Says Hello
Note right of Lucy: Lucy thinks\nabout it
Lucy-->Bob: How are you?
Bob->>Lucy: I am good thanks!
```

### End
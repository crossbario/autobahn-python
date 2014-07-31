# Fonts

We are using the following two fonts as Web fonts:

* [Adobe Source Sans Pro](https://github.com/adobe/source-sans-pro)
* [Adobe Source Code Pro](https://github.com/adobe/source-code-pro)

These fonts are available in different formats. **We use the OTF format.**

> Rendering of the same font differs across formats! E.g. on Windows, OTF will render better than TTF.

## Including

```css
@font-face {
   font-family: 'Source Sans Pro';
   src: url('../fonts/SourceSansPro-Regular.otf');
   font-weight: normal;
}

@font-face {
   font-family: 'Source Sans Pro';
   src: url('../fonts/SourceSansPro-It.otf');
   font-weight: normal;
   font-style: italic;
}

@font-face {
   font-family: 'Source Sans Pro';
   src: url('../fonts/SourceSansPro-Semibold.otf');
   font-weight: bold;
}

@font-face {
   font-family: 'Source Sans Pro';
   src: url('../fonts/SourceSansPro-Light.otf');
   font-weight: 300;
}

@font-face {
   font-family: 'Source Code Pro';
   src: url('../fonts/SourceCodePro-Regular.otf');
   font-weight: normal;
}

@font-face {
   font-family: 'Source Code Pro';
   src: url('../fonts/SourceCodePro-Light.otf');
   font-weight: 300;
}

@font-face {
   font-family: 'Source Code Pro';
   src: url('../fonts/SourceCodePro-Semibold.otf');
   font-weight: bold;
}
```

## Font Settings

The default font family and size should be set on the `body` element:

```css
body {
   font-family: "Source Sans Pro", sans-serif;
   font-size: 16px;
   line-height: 1.428571429;
   color: #333;
   background-color: #fff;
}

code, kbd, pre, samp, span.pre {
   font-family: 'Source Code Pro', monospace;
   font-size: 13px;
}
```

The font family should not be overridden elsewhere.

The font size of subsequent elements should then be set relative to the base size using `em`

```css
h1 {
   font-size: 2em;
}
```

# Headings

The default headings styles:

```css
h1, h2, h3 {
   font-weight: 300;
   color: #027eae;
}

h4, h5, h6 {
   color: #027eae;
}

h1 {
   font-size: 2em;
   margin: .67em 0;
}

h2 {
   font-size: 1.5em;
   margin: .75em 0;
}

h3 {
   font-size: 1.17em;
   margin: .83em 0;
}

h4 {
   font-size: 1em;
   margin: 1.12em 0;
}

h5 {
   font-size: .83em;
   margin: 1.5em 0;
}

h6 {
   font-size: .75em;
   margin: 1.67em 0;
}
```

## Lists

```css
ul, ol {
   line-height: 1.6em;
}
```

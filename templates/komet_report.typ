// KOMET Report Typst Template
// Renders markdown exported from Jupyter notebook

#import "@preview/cmarker:0.1.8"

// Page setup
#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 2.5cm, right: 2.5cm),
  numbering: "1",
  header: context {
    if counter(page).get().first() > 1 [
      #set text(size: 9pt, fill: luma(100))
      KOMET Project – Open Metadata Evaluation Report
      #h(1fr)
      #datetime.today().display("[month repr:long] [year]")
    ]
  }
)

// Typography
#set text(
  lang: "en",
  size: 11pt
)

#show raw: set text(size: 9pt)

#show raw.where(block: false): text.with(
  fill: rgb("#c7254e"),
  weight: "regular"
)

#show raw.where(block: true): block.with(
  fill: luma(245),
  inset: 10pt,
  radius: 4pt,
  width: 100%,
)

// Headings
#show heading.where(level: 1): h => {
  set text(size: 18pt, weight: "bold")
  v(0.5em)
  h
  v(0.3em)
}

#show heading.where(level: 2): h => {
  set text(size: 14pt, weight: "bold")
  v(0.4em)
  h
  v(0.2em)
}

#show heading.where(level: 3): h => {
  set text(size: 12pt, weight: "bold")
  v(0.3em)
  h
  v(0.1em)
}

// Tables
#let frame(stroke) = (x, y) => (
  left: none,
  right: none,
  top: if y < 2 { stroke } else { 0pt },
  bottom: stroke,
)

#set table(
  stroke: frame(0.5pt + luma(150)),
  inset: 8pt,
  fill: (x, y) => if y == 0 { luma(240) } else { none },
)

#show table.cell: set text(size: 10pt)

// Links
#show link: underline
#show link: set text(fill: rgb("#0366d6"))

// Figures and images
#show figure.caption: set text(size: 10pt)

#show image: img => {
  align(center, img)
}

// Title page
#align(center)[
  #v(3cm)
  #text(size: 24pt, weight: "bold")[KOMET Project]
  #v(0.5cm)
  #text(size: 16pt)[Open Metadata Evaluation Report]
  #v(1cm)
  #text(size: 12pt, fill: luma(100))[
    Tracking contributions to OpenCitations and Wikidata
  ]
  #v(2cm)
  #text(size: 11pt)[
    #datetime.today().display("[month repr:long] [year]")
  ]
  #v(1cm)
  #line(length: 50%, stroke: 0.5pt + luma(200))
  #v(0.5cm)
  #text(size: 10pt, fill: luma(100))[
    Generated from komet_evaluation.ipynb
  ]
]

#pagebreak()

// Render the markdown content with custom image handler
#let img = image
#cmarker.render(
  read("report.md"),
  scope: (
    image: (path, alt: none) => {
      img(path, alt: alt)
    },
  )
)

// Footer with funding acknowledgment
#v(1fr)
#line(length: 100%, stroke: 0.5pt + luma(200))
#v(0.3cm)
#set text(size: 9pt, fill: luma(100))
This work is funded by the German Federal Ministry of Education and Research (BMBF) under grant number 16TOA039.

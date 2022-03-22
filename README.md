# Kleist's Embedded Narrations

[![DOI](https://zenodo.org/badge/427284167.svg)](https://zenodo.org/badge/latestdoi/427284167)

This repository contains the annotation data used for my PhD thesis
(*Zur Annotation intradiegetischen Erzählens. Binnenerzählungen im literarischen Werk Heinrich von Kleists*).
Additionaly, the notebook `explore_annotations.ipynb` provides a quick overview of the annotations including network vizualizations.
It has to be used within the cloned repository.

**Alternatively, visit the [annotation dashboard](http://kleist-dashboard.herokuapp.com/) to explore the annotations.**

## Overview and Ressources

- `./AnnotationsDramas/`: Annotations of character speech and embedded narrations in Heinrich von Kleist's dramas
- `./AnnotationsNovellas/`: Annotations of character speech and embedded narrations in Heinrich von Kleist's novellas
- `./Texts/Dramas/`: Plain Texts of Kleist's dramas. Source: [GerDraCor](https://dracor.org/ger)
- `./Texts/Novellas/`: Plain Texts of Kleist's novellas. Source: [TextGrid](https://textgrid.de/de/digitale-bibliothek)
- `./narrview/`: Small Python package for visualization of narratological annotations using Plotly
- `./explore_annotations.ipynb`: Jupyter Notebook for annotation exploration

## Requirements for the Jupyter Notebook / `narrview`

- python>=3.5
- pandas==1.3.2
- plotly==4.14.3

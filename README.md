# ColorOS Custom Icon Resource Library

- [中文 (Chinese)](README.md)
- [English](README.md)

This repository contains custom icon resources for ColorOS.

It includes classic, dark mode, Material, and Monet dynamic color icons.

[Preview URL](https://coloros.github.io/ColorIcons/icons)

## Features

- Full-style adaptation: Supports three visual styles — Classic, Monet, and Material
- Multi-dimensional layouts: Compatible with multiple icon sizes in ColorOS 16, supporting 1x1, 1x2, 2x1, and 2x2 formats
- Automated build: Built-in Python scripts to automatically generate preview pages and resource manifests

## Directory Structure

```
├── global # Global shared resources
├── packages # Core icon library (named by application package name)
│ └── com.example # Example package name
│ ├── monochrome.svg
│ └── recfg.svg
├── scripts # Automation scripts (HTML/Manifest/Index generation)
└── README.md
```

## Contribution Guidelines

When adapting a new application, create a new folder under the `packages` directory using the package name, and follow the specifications below:

### 1. Size Specifications

| Size | Pixels  |
| ---- | ------- |
| 1x1  | 240x240 |
| 1x2  | 240x820 |
| 2x1  | 820x240 |
| 2x2  | 704x704 |

### 2. File Naming Rules

- Classic icons: background `recbg.svg` / foreground `recfg.svg` (supports all sizes)
- Dark mode: foreground only `rec_night.svg` (supports all sizes)
- Monet icons: `monochrome.svg` (supports all sizes)
- Material icons: `mat.svg` (only supports 1x1)

> Naming example: To adapt a 2x2 Monet icon, name it `monochrome_2x2.svg`.

## Disclaimer

All application icons and related visual assets belong to their respective original developers or copyright holders.  
This repository only provides secondary adaptations and format adjustments for use within the ColorOS ecosystem, and does not claim ownership of any original icon designs.

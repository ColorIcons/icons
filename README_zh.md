# ColorOS 自定义图标资源库

- [中文 (Chinese)](README.md)
- [English](README.md)

本仓库包含 ColorOS 的自定义图标资源

包含经典、暗色、材料（Material）以及莫奈（Monet）动态色彩图标。

[预览地址](https://coloros.github.io/ColorIcons/icons)

## 特性

- 全形态适配：支持经典、莫奈、材料三种视觉风格
- 多维布局：适配ColorOS 16系统多种图标大小，支持 1x1, 1x2, 2x1, 2x2 四种尺寸。
- 自动化构建：内置 Python 脚本，支持自动生成预览页面及资源清单。

## 目录结构

```
├── global           # 全局通用资源
├── packages         # 核心图标库（以应用包名命名）
│   └── com.example  # 示例包名
│       ├── monochrome.svg
│       └── recfg.svg
├── scripts          # 自动化脚本 (HTML/Manifest/Index 生成)
└── README.md
```

## 贡献指南

适配新应用时，请在 packages 目录下新建包名文件夹，并参考以下规范：

1. 尺寸规范
   | 尺寸 | 像素 |
   | --- | --- |
   | 1x1 | 240x240 |
   | 1x2 | 240x820 |
   | 2x1 | 820x240 |
   | 2x2 | 704x704 |

2. 文件命名规则

- 经典图标：背景 recbg.svg / 前景 recfg.svg（支持所有尺寸）
- 暗色模式：仅需前景 rec_night.svg（支持所有尺寸）
- 莫奈图标：monochrome.svg（支持所有尺寸）
- 材料图标：mat.svg（仅支持 1x1 ）

> 命名示例：如需适配 2x2 的莫奈图标，命名为 monochrome_2x2.svg。

## 免责声明

所有应用图标及相关视觉资产均归其各自的原始开发者或版权持有者所有。  
本仓库仅提供在ColorOS生态系统内使用的二次改编和格式调整，不声明对任何原始图标设计拥有所有权。

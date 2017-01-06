# Roaring analysis

This project is a performance analysis of the C implementation of **Roaring Bitmaps**. We will focus on one operation: the union between two roaring bitmaps.
This takes place in the Scientific Methodology and Performance Evaluation (SMPE) course of the Grenoble Alpes University.

  - C implementation: https://github.com/RoaringBitmap/CRoaring
  - SMPE course: https://github.com/alegrand/SMPE

## About roaring bitmaps

To be completed.

## Reproduce this work

Laptop used to get the results:
  - CPU: Intel Core i7-5600U
  - RAM: 16GB
  - OS:  Ubuntu 16.04 (Linux 4.4.0-57, gcc 5.4.0)

Clone the repositories:
```bash
git clone --recursive https://github.com/Ezibenroc/roaring_analysis.git
```

Generate the results for the preliminary analysis, with 1024 experiments, output the results in results.csv (about one hour with the described laptop):
```bash
./preliminary_runner.py -n 1024 results.csv
```

## [Preliminary Analysis](preliminary_analysis.ipynb)

This is our first analysis. The aim is to find which factors have a significative impact on the performances.

## [Size and density analysis](size_density_analysis.ipynb)

We have identified the different optimizations that have an impact on performances.

We will now analyze the performances of roaring bitmap unions for various sizes and densities.

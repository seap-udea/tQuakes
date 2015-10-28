#!/bin/bash

for plot in plots/stats/*.py
do
    python $plot
done

for plot in plots/analysis/*.py
do
    python $plot
done

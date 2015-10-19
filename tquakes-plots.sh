#!/bin/bash

for plot in plots/stats/*.py
do
    python $plot
done

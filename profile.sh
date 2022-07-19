#!/bin/bash
mkdir -p profile
python3 -m cProfile -s tottime ecg_viewer.py > profile/$(date +%s).txt

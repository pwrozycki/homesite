#!/bin/bash

export PYTHONPATH=/home/przemas/Desktop/homesite/mysite
PYTHON=/home/przemas/.virtualenvs/uwsgi/bin/python

cd $PYTHONPATH
for task in common/collectionutils/renamer.py \
            common/collectionutils/indexer.py \
            common/collectionutils/thumbnailer.py
do
    echo "Running $task"
    if ! $PYTHON $task
    then
        exit 1
    fi
done



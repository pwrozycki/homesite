#!/bin/bash

export PYTHONPATH=%PROJECT_ROOT%/mysite
PYTHON=%VIRTUALENV%/bin/python

cd $PYTHONPATH
for task in common/collectionutils/renamer.py \
            common/collectionutils/thumbnailer.py \
            common/collectionutils/indexer.py
do
    echo "Running $task"
    if ! $PYTHON $task
    then
        exit 1
    fi
done



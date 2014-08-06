#!/bin/bash

export PYTHONPATH=%PROJECT_ROOT%/mysite
PYTHON=%UWSGI_ROOT%/bin/python

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



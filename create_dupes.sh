#!/bin/bash

content="hello"

for i in {1..5}
do
    echo $content >>$i
done

#!/bin/bash

awk 'BEGIN {OFS=":"}{print NR,$1,$2}' arr.dat 

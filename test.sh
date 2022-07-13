#!/bin/bash
for i in {1..2}
do
    #rm -r www.daraz.pk
    #bash affordability_report https://www.daraz.pk 0.80 0 0 0 0.1
    #rm -r www.daraz.pk
    #bash affordability_report https://www.daraz.pk 0.80 0 0.01 0 0.1
    #rm -r www.daraz.pk
    #bash affordability_report https://www.daraz.pk 0.80 0 0.01 0.01 0.1
    #rm -r www.daraz.pk
    #bash affordability_report https://www.daraz.pk 0.80 0.01 0.01 0 0.1
    #rm -r www.daraz.pk
    #bash affordability_report https://www.daraz.pk 0.80 0.01 0.01 0.01 0.1
    

    rm -r www.daraz.pk
    bash affordability_report https://www.daraz.pk 0.80 0 0.1 0 0.1
    rm -r www.daraz.pk
    bash affordability_report https://www.daraz.pk 0.80 0 0.1 0.01 0.1
    rm -r www.daraz.pk
    bash affordability_report https://www.daraz.pk 0.80 0.01 0.1 0 0.1
    rm -r www.daraz.pk
    bash affordability_report https://www.daraz.pk 0.80 0.01 0.1 0.01 0.1
    
done

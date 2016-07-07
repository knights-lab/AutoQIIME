#!/bin/bash -x

# Usage: make.output.sh workingdir otutable ggtreefile [raredepth]

DIR=$1
OTU=$2
TREE=$3

SUMMARY="$DIR/otu_summary.txt"
TAXADIR="$DIR/taxonomy"
ALPHA="$DIR/alpha.txt"
BETA="$DIR/beta"

if [ $# -eq 4 ]; then
	DEPTH=$4
	OTU_RARE="$DIR/otu_rare.biom"
	single_rarefaction.py -i "$OTU" -o "$OTU_RARE" -d $DEPTH
	if [ $? -ne 0 ]; then
    	exit $?
	fi
	OTU="$OTU_RARE"
	SUMMARY="$DIR/otu_summary_rare.txt"
	TAXADIR="$DIR/taxonomy_rare"
	ALPHA="$DIR/alpha_rare.txt"
	BETA="$DIR/beta_rare"
fi

echo "Summarizing OTU table..."
biom summarize-table -i "$OTU" -o "$SUMMARY"
if [ $? -ne 0 ]; then
    exit $?
fi

echo "Summarizing Taxonomy..."
summarize_taxa.py -i "$OTU" -o "$TAXADIR"
if [ $? -ne 0 ]; then
    exit $?
fi

echo "Calculating Alpha Diversity..."
alpha_diversity.py -i "$OTU" -t "$TREE" -o "$ALPHA"
if [ $? -ne 0 ]; then
    exit $?
fi

echo "Calculating Beta Diversity..."
beta_diversity.py -i "$OTU" -m unweighted_unifrac,weighted_unifrac,bray_curtis -o "$BETA" -t "$TREE"
if [ $? -ne 0 ]; then
    exit $?
fi

#!/usr/bin/env python3

'''
This script reads a GFF3 file and FASTA file (or FASTA embedded in the GFF) and
checks the translation of all CDS for internal stops.  The output is like:

    Total mRNAs found:4091
    mRNAs with embedded stops: 895

The script checks and removes terminal stop codons, so these will not be reported
if stops are found at the very end of the reading frame.

Follow the GFF3 specification!

Author:  Joshua Orvis
'''

import argparse
import os
import biocodegff
import biocodeutils


def main():
    parser = argparse.ArgumentParser( description='Checks the CDS features against a genome sequence to report/correct phase columns.')

    ## output file to be written
    parser.add_argument('-i', '--input_file', type=str, required=True, help='Path to the input GFF3' )
    parser.add_argument('-g', '--genome_fasta', type=str, required=False, help='Optional.  You must specify this unless the FASTA sequences for the molecules are embedded in the GFF')
    args = parser.parse_args()

    (assemblies, features) = biocodegff.get_gff3_features( args.input_file )

    # deal with the FASTA file if the user passed one
    if args.genome_fasta is not None:
        process_assembly_fasta(assemblies, args.genome_fasta)

    total_mRNAs = 0
    mRNAs_with_stops = 0

    # If this is set to the ID of any particular mRNA feature, the CDS and translation will be printed for it.
    debug_mRNA = None
        
    for assembly_id in assemblies:
        for gene in assemblies[assembly_id].genes():
            for mRNA in gene.mRNAs():
                coding_seq = mRNA.get_CDS_residues()
                total_mRNAs += 1

                if debug_mRNA is not None and mRNA.id == debug_mRNA:
                    print("CDS:{0}".format(coding_seq))

                if biocodeutils.translate(coding_seq).rstrip('*').count('*') > 0:
                    mRNAs_with_stops += 1
                    if debug_mRNA is not None and mRNA.id == debug_mRNA:
                        print("TRANSLATION WITH STOP ({1}): {0}".format(biocodeutils.translate(coding_seq), mRNA.id) )


    print("\nTotal mRNAs found:{0}".format(total_mRNAs))
    print("mRNAs with embedded stops: {0}".format(mRNAs_with_stops))


def process_assembly_fasta(mols, fasta_file):
    fasta_seqs = biocodeutils.fasta_dict_from_file( fasta_file )

    for mol_id in mols:
        # check if the FASTA file provides sequence for this
        if mol_id in fasta_seqs:
            mol = mols[mol_id]
            mol.residues = fasta_seqs[mol_id]['s']
            mol.length   = len(mol.residues)
        

if __name__ == '__main__':
    main()






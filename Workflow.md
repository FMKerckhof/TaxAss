# TaxASS workflow

Fancy markdown version of `workflow.txt`.
The TaxASS workflow assigns taxonomy to a fasta file of otu sequences using both 
a small, custom taxonomy database and a large general database.

## Summary of Steps and Commands

Unless stated otherwise, all commands below are entered in terminal window.

1. Background and why we chose this workflow
2. Format files (textwrangler or bash)
    + For the Green Genes (GG) database as general.taxonomy:
      ```bash
       sed 's/ //g' < general.taxonomy >NoSpaces
       sed 's/$/;/' < NoSpaces >EndLineSemicolons
       mv EndLineSemicolons general.taxonomy
       rm NoSpaces
      ```
    + For aligned fasta files:
      ```Shell
       sed 's/-//g' <aligned.fasta >otus.fasta
      ```
3. Make BLAST database file (blast+)



# Dependencies

* Mothur
* The NCBI blast+ suite
* R (preferably with the reshape package installed)
* Python
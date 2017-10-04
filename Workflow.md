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
    + For mothur .count_table as OTU table:
      ```bash
       Rscript reformat_mothur_OTU_tables.R StupidLongMothurName.count_table count_table otus.abund
      ```
3. make BLAST database file (blast+)
  ```bash
	 makeblastdb -dbtype nucl -in custom.fasta -input_type fasta -parse_seqids -out custom.db
  ```
4. run BLAST (blast+)
  ```bash
	 blastn -query otus.fasta -task megablast -db custom.db -out otus.custom.blast -outfmt 11 -max_target_seqs 5
  ```
	

3. reformat blast results (blast)
	blast_formatter -archive otus.custom.blast -outfmt "6 qseqid pident length qlen qstart qend" -out otus.custom.blast.table

4. correct BLAST pident (R)
	Rscript calc_full_length_pident.R otus.custom.blast.table otus.custom.blast.table.modified

5. filter BLAST results (R)
	Rscript filter_seqIDs_by_pident.R otus.custom.blast.table.modified ids.above.98 98 TRUE 
	Rscript filter_seqIDs_by_pident.R otus.custom.blast.table.modified ids.below.98 98 FALSE

6. check that BLAST settings are appropriate (R)
	mkdir plots
	Rscript plot_blast_hit_stats.R otus.custom.blast.table.modified 98 plots

7. recover sequence IDs left out of blast (python, bash)
	python find_seqIDs_blast_removed.py otus.fasta otus.custom.blast.table.modified ids.missing
	cat ids.below.98 ids.missing > ids.below.98.all
	
8. create fasta files of desired sequence IDs (python)
	python create_fastas_given_seqIDs.py ids.above.98 otus.fasta otus.above.98.fasta
	python create_fastas_given_seqIDs.py ids.below.98.all otus.fasta otus.below.98.fasta

9. assign taxonomy (mothur)
	mothur "#classify.seqs(fasta=otus.above.98.fasta, template=custom.fasta,  taxonomy=custom.taxonomy, method=wang, probs=T, processors=2, cutoff=0)"
	mothur "#classify.seqs(fasta=otus.below.98.fasta, template=general.fasta, taxonomy=general.taxonomy, method=wang, probs=T, processors=2, cutoff=0)"

10. combine taxonomy files (bash)
	cat otus.above.98.custom.wang.taxonomy otus.below.98.general.wang.taxonomy > otus.98.taxonomy

11. assign taxonomy with general database only (mothur, bash)
	mothur "#classify.seqs(fasta=otus.fasta, template=general.fasta, taxonomy=general.taxonomy, method=wang, probs=T, processors=2, cutoff=0)"
	cat otus.general.wang.taxonomy > otus.general.taxonomy

11.5 OPTIONAL- feeds into Database_Improvement_Workflow
	assign taxonomy to custom database with general database (mothur, bash)
	mothur "#classify.seqs(fasta=custom.fasta, template=general.fasta, taxonomy=general.taxonomy, method=wang, probs=T, processors=2, cutoff=0)"
	cat custom.general.wang.taxonomy custom.general.taxonomy

12. reformat taxonomy files (bash)
	sed 's/[[:blank:]]/\;/' <otus.98.taxonomy >otus.98.taxonomy.reformatted
	mv otus.98.taxonomy.reformatted otus.98.taxonomy
	sed 's/[[:blank:]]/\;/' <otus.general.taxonomy >otus.general.taxonomy.reformatted
	mv otus.general.taxonomy.reformatted otus.general.taxonomy
	
13. compare taxonomy files (R)
	mkdir conflicts_98
	Rscript find_classification_disagreements.R otus.98.taxonomy otus.general.taxonomy ids.above.98 conflicts_98 98 85 70
	
14. OPTIONAL: choose appropriate pident cutoff (R)
	note: you have to repeat steps 5, 7-10, & 12-13 with multiple pident cutoffs to do this step
	Rscript plot_classification_disagreements.R otus.abund plots regular NA NA conflicts_94 ids.above.94 94 conflicts_96 ids.above.96 96 conflicts_98 ids.above.98 98

15. generate final taxonomy file (R)
	Rscript find_classification_disagreements.R otus.98.taxonomy otus.general.taxonomy ids.above.98 conflicts_98 98 85 70 final

15.5 OPTIONAL: plot benefits of using this workflow (R, mothur, bash)
	a. Improvement over general database only:
		Rscript plot_classification_improvement.R final.taxonomy.pvalues final.general.pvalues total.reads.per.seqID.csv plots final.taxonomy.names final.general.names
	b. Improvement over custom database only:
		mothur "#classify.seqs(fasta=otus.fasta, template=custom.fasta, taxonomy=custom.taxonomy, method=wang, probs=T, processors=2, cutoff=0)"
		cat otus.custom.wang.taxonomy > otus.custom.taxonomy
		sed 's/[[:blank:]]/\;/' <otus.custom.taxonomy >otus.custom.taxonomy.reformatted
		mv otus.custom.taxonomy.reformatted otus.custom.taxonomy
		mkdir conflicts_forcing
		Rscript find_classification_disagreements.R otus.custom.taxonomy otus.98.85.70.taxonomy ids.above.98 conflicts_forcing NA 85 70 forcing
		Rscript plot_classification_disagreements.R otus.abund plots conflicts_forcing otus.custom.85.taxonomy otus.98.85.70.taxonomy

16. tidy up (bash)
	rm custom.db.* custom.8mer custom.custom* custom.tree* general.8mer general.general* general.tree* *wang* mothur.*.logfile otus.custom.blast* ids* otus.below*.fasta otus.above*.fasta otus.[0-9][0-9].taxonomy otus.[0-9][0-9][0-9].taxonomy otus.general.taxonomy otus.custom.taxonomy otus.custom.[0-9]* custom.general* *pvalues total* final*names
	mkdir scripts ; mv *.py *.R *.sh scripts
	mkdir analysis ; mv conflicts* plots analysis
	mkdir data ; mv otus* data
	mkdir databases ; mv *.taxonomy *.fasta databases


# Dependencies

* Mothur
* The NCBI blast+ suite
* R (preferably with the reshape package installed)
* Python
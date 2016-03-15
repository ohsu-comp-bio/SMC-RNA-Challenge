Example scripts:

../build/bin/fusionToolEvaluator -t truth.bedpe -r res.bedpe -g ensembl.hg19.txt -s rulefile.txt -o outputfile.tsv

../build/bin/fusionToolEvaluator -t truth.bedpe -r res.bedpe -g ensembl.hg19.txt -s rulefile.txt -o outputfile.tsv -b 1 -p 15,15,20,12,12,14


Gene Annotation:

Enemble Genes:
1.click: Table Browser
2.click: To reset all user cart settings (including custom tracks), click here. 
3.choose: assembly:  Feb. 2009 (GRCh37/hg19) 
4.choose: track: Ensembl Genes
5.choose: output format: selected fields from primary and related tables
6. click: get output
7. choose: Select Fields from hg19.ensGene: name, chrome, strand, txStart, tend, cdsStart, cdsEnd, exonCount, exonStarts, exonEnds
8 choose: Linked Tables: ensemblToGeneName
9. click: allow selection from checked tables
10. choose: value | alternate gene name
11. click: get output

GENCODE Genes V19:
1. click Table Browser
2. To reset all user cart settings (including custom tracks), click here.
3. assembly:  Feb. 2009 (GRCh37/hg19) 
4. track GENCODE Genes V19:
5. output format: selected fields from primary and related tables
click: get output
7. choose: 
6. choose: Select Fields from hg19.wgEncodeGencodeBasicV19: name, chrome, strand, txStart, tend, cdsStart, cdsEnd, exonCount, exonStarts, exonEnds
8 choose: Linked Tables: Basic set of attributes associated with all Gencode transcripts.
9. click: allow selection from checked tables
10. choose: geneName
11. click: get output

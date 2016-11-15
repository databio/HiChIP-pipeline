microtest:
	python $$CODEBASE/hichip-pipeline/pipelines/hichip.py\
	 -I $$MICROTEST/data/hichip.bam\
	 -G hg38 -O $$HOME/scratch\
	 -S test --single-or-paired paired -R
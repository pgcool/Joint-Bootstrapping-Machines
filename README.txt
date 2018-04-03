
Joint Bootstrapping Machines for High Confidence Relation Extraction
	
	In conference proceedings of NAACL-HLT 2018.
	
	
Dependecies:

Python 2.7, Numpy, NLTK, Gensim, jellyfish, whoosh, etc.
	
Directory Structure:

Joint-Bootstrapping-Machines

	./resources
		freebase-easy-14-04-14
			freebase_facts.txt (Download from url http://freebase-easy.cs.uni-freiburg.de/dump/)
			
	./data
		input
			sentences.txt (Download corpus from url: https://drive.google.com/file/d/0B0CbnDgKi0PyM1FEQXJRTlZtSTg/view)
		output
			BREE
				REL_ACQUIRED_ORG_ORG
					relationships_baseline.txt : The output file containing a list of the relationships extracted from BREE system)
			BRET
				REL_ACQUIRED_ORG_ORG
					relationships_config5.txt : The output file containing a list of the relationships extracted from BRET system)
			BREJ
				REL_ACQUIRED_ORG_ORG
					relationships_config9.txt : The output file containing a list of the relationships extracted from BREJ system)

	./code
		automatic_evaluation
			index_dir : Directory of corpus-index
			
			index_whoosh.py : To create corpus-index in directory index_dir.
			
			Sentence.py : To extract entities infomation, clean and filter.
			
			easy_freebase_clean.py : To collect relationships facts from Freebase and prepare databases.
			
			large_scale_evaluation_freebase.py : To automatically evaluate relation extraction systems on large-scale (https://akbcwekex2012.files.wordpress.com/2012/05/8_paper.pdf).
			

Usage (Evaluation):
 
	python large_scale_evaluation_freebase.py threshold system_output rel_type database root_dir corpus-index
	
	
	Example:

	cd Joint-Bootstrapping-Machines/code/automatic_evaluation
 
	python large_scale_evaluation_freebase.py 0.5 ../../data/output/BREE/REL_ACQUIRED_ORG_ORG/relationships_baseline.txt acquired ../../resources/freebase-easy-14-04-14/freebase_facts.txt ../../data ../../data/input/sentences.txt ./index_dir
	
	
	
	
	
	
	
	
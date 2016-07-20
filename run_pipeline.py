import pypiper, os
pypiper_out = "pypiper_output"
hicpro_out = os.path.join(pypiper_out,"hicpro")
pipeline = pypiper.PipelineManager(name="hichip_pipeline", outfolder=pypiper_out)
inputfolder = "/home/cdai/projects/HiChIP_test/HiC-Pro_test/test_data"
configfile = "config.txt"
cmd = "HiC-Pro -i " + inputfolder + " -o " + hicpro_out + " -c " + configfile
target = os.path.join(pypiper_out, "outfile.txt")
pipeline.run(cmd, target)
pipeline.stop_pipeline()

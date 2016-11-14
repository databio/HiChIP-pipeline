#!/usr/bin/env python

from argparse import ArgumentParser
import pypiper, os

parser = ArgumentParser(description='Pipeline')
parser = pypiper.add_pypiper_args(parser, all_args = True)

args = parser.parse_args()

 # it always paired seqencung for ATACseq
if args.single_or_paired == "paired":
	args.paired_end = True
else:
	args.paired_end = False

outfolder = os.path.abspath(os.path.join(args.output_parent, args.sample_name))
pm = pypiper.PipelineManager(name="hichip", outfolder = outfolder, args = args)
ngstk = pypiper.NGSTk(pm=pm)

pm.config.tools.scripts_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tools")

# Convenience alias 
#tools = pm.config.tools
param = pm.config.parameters
res = pm.config.resources
tools = pm.config.tools

param.outfolder = outfolder
raw_folder = os.path.join(param.outfolder, "raw/")
fastq_folder = os.path.join(param.outfolder, "fastq/")

pm.timestamp("### Merge/link and fastq conversion: ")
# This command will merge multiple inputs so you can use multiple sequencing lanes
# in a single pipeline run. 
local_input_files = ngstk.merge_or_link([args.input, args.input2], raw_folder, args.sample_name)
cmd, out_fastq_pre, unaligned_fastq = ngstk.input_to_fastq(local_input_files, args.sample_name, args.paired_end, fastq_folder)
pm.run(cmd, unaligned_fastq, 
	follow=ngstk.check_fastq(local_input_files, unaligned_fastq, args.paired_end))
pm.clean_add(out_fastq_pre + "*.fastq", conditional = True)
print(local_input_files)


# Run HiC-Pro
pm.timestamp("### Run HiC-Pro")
hicpro_out = os.path.join(param.outfolder,"hicpro")
#pm.make_sure_path_exists(hicpro_out)  # don't do this! it stalls hicpro!
# Re-write hicpro config template
configfile = "config.txt"
import sys
cfg_template = os.path.join(os.path.dirname(sys.argv[0]), configfile)
local_hicpro_cfg = os.path.join(param.outfolder, "hicpro_config.txt")

# build variable dict with config options
variables_dict = {}
variables_dict["N_CPU"] = pm.cores
variables_dict["REFERENCE_GENOME"] = args.genome_assembly

# hichip wants these in a subfolder...
fastq_subfolder = os.path.join(fastq_folder, args.sample_name)
pm.make_sure_path_exists(fastq_subfolder)

#cmd = "ln -s " + out_fastq_pre + "*.fastq" + " " +  fastq_subfolder
cmd = "ln -rfs " + fastq_folder + "*fastq " + fastq_subfolder
pm.run(cmd, fastq_subfolder)

print("Using template: " + cfg_template + " to produce config " + local_hicpro_cfg)
with open(cfg_template, 'r') as handle:
	filedata = handle.read()
# fill in submit_template with variables
for key, value in variables_dict.items():
	# Here we add brackets around the key names and use uppercase because
	# this is how they are encoded as variables in the template.
	filedata = filedata.replace("{" + str(key).upper() + "}", str(value))

# save config file
with open(local_hicpro_cfg, 'w') as handle:
	handle.write(filedata)

target = os.path.join(hicpro_out, "finished.flag")
cmd = tools.hicpro + " -i " + fastq_folder + " -o " + hicpro_out + " -c " + local_hicpro_cfg
cmd2 = "touch " + target

pm.run([cmd, cmd2], target)

pm.timestamp("### Format output for Juicer")
# Now format output for juicer

valid_pairs = os.path.join(hicpro_out, "hic_results/data/", args.sample_name, args.sample_name + "_allValidPairs")

valid_pairs_out = valid_pairs + "_sorted.gz"

cmd = os.path.join(tools.scripts_dir, "preJuice.py") + " -i " + valid_pairs
cmd += " | sort --parallel=" + pm.cores
cmd += " -k12,12 - | cut -f12 --complement | gzip - > " + valid_pairs_out

pm.run(cmd, valid_pairs_out)

# produce hic file for input to Juicer and visualization
juicebox_out = os.path.join(hicpro_out, args.sample_name + ".hic")
cmd = tools.java + " -Xmx" + pm.javamem
cmd += " -jar " + tools.juiceboxtools
cmd += " pre " + valid_pairs_out 
cmd += " " + juicebox_out
cmd += " " + args.genome_assembly

pm.run(cmd, juicebox_out)






pm.stop_pipeline()

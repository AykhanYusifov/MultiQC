#!/usr/bin/env python

""" MultiQC module to parse output from HTStream """

from __future__ import print_function
from collections import OrderedDict
import logging
import re, json

from . import stats
from multiqc import config
from multiqc.modules.base_module import BaseMultiqcModule


#################################################

# Logger Initialization
log = logging.getLogger(__name__)

class MultiqcModule(BaseMultiqcModule):

	def __init__(self):

		self.sample_statistics = {}

		# Initialise the parent object
		super(MultiqcModule, self).__init__(name='HTStream',
		anchor='htstream', href='https://ibest.github.io/HTStream/',
		info=" quality control and processing pipeline for High Throughput Sequencing data ")

		self.data = OrderedDict()

		 # iterates through files found by "find_log_files" (located in base_module.py)
		for file in self.find_log_files('htstream'):
			self.add_data_source(file)
			self.s_name = file['s_name'] # sample name
			self.file_data = self.parse_json(file['f']) # parse stats file. Should return directory of apps and their stats 

			self.data[self.s_name] = self.file_data

			
		self.data = self.ignore_samples(self.data)

		if len(self.data) == 0:
			raise UserWarning

		self.parse_stats(self.data) 

		# 
		#self.general_stats_addcols(self.data)

		#
		#self.sample_statistics[self.s_name] = self.file_data 

	#################################################
	# Json and stats parsing functions

	def parse_json(self, f):

		return json.loads(f)


	def parse_stats(self, json):

		self.apps = {
            'AdapterTrimmer': stats.AdapterTrimmer(),
            'CutTrim': stats.CutTrim(),
            'Overlapper': stats.Overlapper(),
            'QWindowTrim': stats.QWindowTrim(),
            'NTrimmer':stats.NTrimmer(),
            'PolyATTrim': stats.PolyATTrim(),
            'SeqScreener': stats.SeqScreener(),
            'SuperDeduper': stats.SuperDeduper(),
            'Primers': stats.Primers(),
    		}

		for app in self.apps.keys():
			stats_dict = OrderedDict()

			for key in json.keys():

				for subkey in json[key].keys():

					if app in subkey:
						stats_dict[key] = json[key][subkey]

			if len(stats_dict.keys()) != 0:

				plot = self.apps[app].execute(stats_dict)

				section = "hts_" + app

				self.add_section(name = section,
								 plot = plot)

				# self.add_section(name = 'HTStream',
				# 				 anchor = section,
				# 				 description = 'This plot shows some really nice data.',
				# 				 helptext = 'This longer string (can be **markdown**) helps explain how to interpret the plot',
				# 				 plot = plot
				# 				 )

			#self.add_section( plot = self.htseq_counts_chart() )


#!/usr/bin/env python3

# TODO: Add a -t option for verification only if files have unicode text.
#       This way, after a conversion one can verifies if everything went fine.
# TODO: Add translation to common unicode symbols such as ß.
#       Treat all unicode would be a mad, so let's treat the common unicode ones, not greek chars.

import unittest
import argparse
import os
import fnmatch
import logging
import string
import unicodedata
import filecmp
import tempfile

logging.basicConfig()
logger = logging.getLogger('main')
logger.setLevel(logging.WARNING)

# constants
DEFAULT_OUTPUT_EXTENSION = '.u2t'

# global variables
parser = None
args = None
unicode_to_ascii_symbol = {\
	'0300': '`',\
	'0301': "'",\
	'0302': '^',\
	'0303': '~',\
	'0304': '=',\
	'0306': 'u',\
	'0307': '.',\
	'0308': '"',\
	'030A': 'r',\
	'030B': 'H',\
	'030C': 'v',\
	'0327': 'c',\
	'0328': 'k',
	}


def main():
	logger.setLevel(logging.INFO)
	for file in range(0, len(args.input_file)):
		logger.info("Processing file %s into %s...", args.input_file[file], args.output_file[file])
		file_conversion(args.input_file[file], args.output_file[file])
	logger.info("Finished processing files. \n")

def create_args_parser():
	'''Creating the command line arguments'''
	global parser
	parser = argparse.ArgumentParser(description='Unicode to (La)TeX')
	parser.add_argument('-i', '--input-file', nargs='*', help='Input file which wants to be converter. If none is passed, process all .tex files in the current directory')
	parser.add_argument('-o', '--output-file', nargs='*', help='Output file with conversion results. If none is passed, outputs a INPUT_FILE' + DEFAULT_OUTPUT_EXTENSION + ' file')

def retrieve_args():
	'''Retrieving the commmand line arguments'''
	global args
	args = parser.parse_args()
	logger.debug('Command Line Arguments: %s', vars(args))
	if args.input_file == None:
		logger.debug('Input files: %s', args.input_file)
		args.input_file = list()
		for file in os.listdir('.'):
			if fnmatch.fnmatch(file, '*.tex'):
				args.input_file.append(file)
			else:
				pass
		if args.input_file == list():
			args.input_file = None
		else:
			pass
	else:
		pass
	logger.debug('Input files: %s', args.input_file)

def create_output_files():
	'''For each file, create string (file name) named after output-file argument'''
	if args.output_file == None or len(args.output_file) == 0:
		if args.input_file == None or len(args.input_file) == 0:
			logger.warning('No input file! Skipping execution')
			exit()
		else:
			args.output_file = list()
			# TODO: could change the proceding instruction as a call to a function
			for file in args.input_file:
				args.output_file.append(file + DEFAULT_OUTPUT_EXTENSION)
				logger.debug('Output files: %s', args.output_file)
	else:
		if len(args.input_file) > len(args.output_file):
			logger.warning('Input files are in greater number than output files: output files without match will receive the default output extension.')
			logger.debug('Output files: %s', args.output_file)
			# TODO: could change the proceding instruction as a call to a function
			for file in args.input_file[len(args.output_file):len(args.input_file)]:
				args.output_file.append(file + DEFAULT_OUTPUT_EXTENSION)
				logger.debug('New output files: %s', args.output_file)
		elif len(args.input_file) < len(args.output_file):
			logger.warning('Output files are in greater number than input files: exceed ones will be ignored.')
			logger.debug('Output files: %s', args.output_file)
			args.output_file = args.output_file[0:len(args.input_file)]
			logger.debug('New output files: %s', args.output_file)

def get_characters(line):
	return list(line)

def is_non_ascii(char):
	if char not in string.printable:
		return True
	else:
		return False

def has_non_ascii(line):
	chars = get_characters(line)
	for character in chars:
		if is_non_ascii(character):
			return True
		else:
			pass
	return False

def unicode_to_ascii(unicode_string):
	logger = logging.getLogger('unicode_to_ascii')
	logger.setLevel(logging.WARNING)
	logger.debug('unicode_string = %s', unicode_string)
	if unicode_string.isnumeric():
		return unicode_to_ascii_symbol[unicode_string]
	elif all(map(lambda x: True if x in string.hexdigits else False, get_characters(unicode_string))):
		return unicode_to_ascii_symbol[unicode_string]
	else:
		None

def unicode_to_latex(char):
	logger = logging.getLogger('unicode_to_latex')
	logger.setLevel(logging.WARNING)
	codes = unicodedata.decomposition(char).split()
	logger.debug('Codes from Unichar Decomposition = %s', codes)
	if len(codes) == 2:
		return '\\' + unicode_to_ascii(codes[1]) + '{' + chr(int(codes[0], 16)) + '}'
	else:
		pass

def line_conversion(line):
	logger = logging.getLogger('line_convertion')
	logger.setLevel(logging.WARNING)
	converted_line = line
	translation_table = dict()
	if has_non_ascii(line):
		for character in get_characters(line):
			if is_non_ascii(character) and character not in translation_table.keys():
				logger.debug("'%s' -> '%s'", character, unicode_to_latex(character))
				translation_table[character] = unicode_to_latex(character)
		converted_line = line.translate(str.maketrans(translation_table))
	else:
		pass
	return converted_line

def file_conversion(original_filename, modified_filename):
	substitute_original = False
	original = open(original_filename, 'r')
	if original_filename == modified_filename:
		modified_filename = original_filename + '.tmp'
		substitute_original = True
	else:
		pass
	modified = open(modified_filename, 'w')
	for line in original.readlines():
		converted_line = line_conversion(line)
		modified.write(converted_line)
	modified.close()
	original.close()
	if substitute_original:
		os.remove(original_filename)
		os.rename(modified_filename, original_filename)
	else:
		pass


class SimpleTest(unittest.TestCase):
	def test_get_each_character(self):
		self.assertEqual(get_characters('This is it.'), ['T','h','i','s',' ','i','s',' ', 'i', 't','.'])

	def test_is_non_ascii(self):
		self.assertEqual(is_non_ascii('a'), False)
		self.assertEqual(is_non_ascii('\n'), False)
		self.assertEqual(is_non_ascii('ã'), True)
		self.assertEqual(is_non_ascii('Ş'), True)
		self.assertEqual(is_non_ascii('ğ'), True)
		self.assertEqual(is_non_ascii('ß'), True)

	def test_has_non_ascii(self):
		self.assertEqual(has_non_ascii('This is it.'), False)
		self.assertEqual(has_non_ascii('This is it.\n'), False)
		self.assertEqual(has_non_ascii('Amanhã choverá na rua.'), True)
		self.assertEqual(has_non_ascii('Morgen wird auf der Straße regen.'), True)
		self.assertEqual(has_non_ascii('Αύριο θα βρέξει στο δρόμο'), True)
		self.assertEqual(has_non_ascii('Yarın sokakta yağmur yağacak.'), True)

	def test_unicode_to_ascii(self):
		self.assertEqual(unicode_to_ascii('0300'), '`')
		self.assertEqual(unicode_to_ascii('0301'), "'")
		self.assertEqual(unicode_to_ascii('0302'), '^')
		self.assertEqual(unicode_to_ascii('0303'), '~')
		self.assertEqual(unicode_to_ascii('TEXT'), None)

	def test_convert_to_latex_two_symbols(self):
		self.assertEqual(unicode_to_latex('ò'), '\\`{o}')
		self.assertEqual(unicode_to_latex('ó'), "\\'{o}")
		self.assertEqual(unicode_to_latex('ô'), '\\^{o}')
		self.assertEqual(unicode_to_latex('ö'), '\\"{o}')
		self.assertEqual(unicode_to_latex('ő'), '\\H{o}')
		self.assertEqual(unicode_to_latex('õ'), '\\~{o}')
		self.assertEqual(unicode_to_latex('ō'), '\\={o}')
		self.assertEqual(unicode_to_latex('ȯ'), '\\.{o}')
		self.assertEqual(unicode_to_latex('ŏ'), '\\u{o}')
		self.assertEqual(unicode_to_latex('š'), '\\v{s}')
		self.assertEqual(unicode_to_latex('ç'), '\\c{c}')
		self.assertEqual(unicode_to_latex('å'), '\\r{a}')
		self.assertEqual(unicode_to_latex('ą'), '\\k{a}')
		self.assertEqual(unicode_to_latex('ḩ'), '\\c{h}')
		self.assertEqual(unicode_to_latex('Ş'), '\\c{S}')
		# self.assertEqual(unicode_to_latex('ø'), '\\o')
		# self.assertEqual(unicode_to_latex('ß'), '\\ss}')
		# self.assertEqual(unicode_to_latex('ł'), '\\l}')

	def test_string_conversion_two_symbols(self):
		self.assertEqual(line_conversion('This is it.'), "This is it.")
		self.assertEqual(line_conversion('This is it.\n'), "This is it.\n")
		self.assertEqual(line_conversion('Amanhã choverá na rua.'), "Amanh\~{a} chover\\'{a} na rua.")
		# self.assertEqual(line_conversion('Morgen wird auf der Straße regen.'), "Morgen wird auf der Stra\sse regen.")
		# self.assertEqual(line_conversion('Αύριο θα βρέξει στο δρόμο'), True)
		# self.assertEqual(line_conversion('Yarın sokakta yağmur yağacak.'), True)

	def test_file_conversion_different_filenames(self):
		logger = logging.getLogger('test_file_conversion_different_filenames')
		logger.setLevel(logging.WARNING)
		original_filename = ''
		modified_filename = ''
		while original_filename == modified_filename:
			original_filename = input("Original filename [default: 'original.tex']: ")
			if original_filename == '':
				original_filename = 'original.tex'
			else:
				pass
			modified_filename = input("Modified filename [default: 'modified.tex']: ")
			if modified_filename == '':
				modified_filename = 'modified.tex'
			else:
				pass
			if original_filename == modified_filename:
				logger.warning('File names must be different!')
		file_conversion(original_filename, modified_filename)
		self.assertFalse(filecmp.cmp(original_filename, modified_filename))
		modified = open(modified_filename, 'r')
		for line in modified.readlines():
			self.assertFalse(has_non_ascii(line))
		modified.close()

	def test_file_conversion_same_filenames(self):
		original_filename = ''
		original_filename = input("Original filename [default: 'original_modified.tex']: ")
		if original_filename == '':
			original_filename = 'original_modified.tex'
		else:
			pass
		file_conversion(original_filename, original_filename)
		modified = open(original_filename, 'r')
		for line in modified.readlines():
			self.assertFalse(has_non_ascii(line))
		modified.close()
		


if __name__ == '__main__':
	create_args_parser()
	retrieve_args()
	create_output_files()
	main()
	# unittest.main()

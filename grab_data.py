# WoC Hackathon's TrackHacks project
# Authors: Alexander Nolte, and Ei Pa Pa Pe-Than

import sys
import os
import math
import pandas as pd
import subprocess
from datetime import datetime

def getCommitContent(inputfile):
	start_from = 0
	woc_commits = pd.read_csv(inputfile, sep=',')
	# remove for start_from
	if start_from == 0:
		woc_commits['tree_content'] = ''
		woc_commits['commit_size'] = 0

	for index, row in woc_commits.iterrows():
		print('index: '+str(index)+' '+str(row['commit_sha'])+' @ '+str(datetime.now().strftime("%H:%M:%S")))
		if index > start_from:
			process = subprocess.Popen('echo '+str(row['commit_sha'])+' | ~/lookup/showCnt commit', shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
			out, err = process.communicate()
			tree_id = out.split('\n', 1)[0]
			if len(tree_id) > 0:
				tree_id = tree_id.split('tree ')[1]
				process = subprocess.Popen('echo '+str(tree_id)+' | ~/lookup/showCnt tree', shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
				out, err = process.communicate()
				tree_content = out.rstrip().split('\n')
				woc_commits.at[index, 'tree_content'] = tree_content
				woc_commits.at[index, 'commit_size'] = len(tree_content)
				if index > start_from+2 and index % 1000 == 0:
					print('***** saving')
					woc_commits.to_csv('woc-commits.csv', sep=',', index=False, encoding='utf-8')

	woc_commits.to_csv('woc-commits.csv', sep=',', index=False, encoding='utf-8')

def getCommitInformation(inputfile):
	# could be nested in getP2C
	woc_commits = pd.read_csv(inputfile, sep=',')
	woc_commits['commit_date'] = ''
	woc_commits['author_id'] = ''
	woc_commits['author_name'] = ''
	woc_commits['author_email'] = ''

	for index, row in woc_commits.iterrows():
		print('index: '+str(index)+' @ '+str(datetime.now().strftime("%H:%M:%S")))
		process = subprocess.Popen('echo '+str(row['commit_sha'])+' | ~/lookup/getValues c2ta', shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		out, err = process.communicate()
		out_array = out.rstrip().split(';')

		author_id = out_array[2]
		woc_commits.at[index, 'commit_date'] = datetime.fromtimestamp(float(out_array[1]))
		woc_commits.at[index, 'author_id'] = author_id
		woc_commits.at[index, 'author_name'] = author_id.split(' <')[0]
		woc_commits.at[index, 'author_email'] = author_id.split(' <')[1].split('>')[0]

	woc_commits.to_csv('woc-commits.csv', sep=',', index=False, encoding='utf-8')

def getC2P(inputfile):
	# could be nested in getP2C
	start_from = 9000

	woc_commits = pd.read_csv(inputfile, sep=',')

	if start_from == 0:
		woc_commits['is_in_other_projects'] = 0
		woc_commits['number_of_other_projects_it_is_in'] = 0
		woc_commits['urls_of_other_projects_it_is_in'] = ''

	for index, row in woc_commits.iterrows():
		print('index: '+str(index)+' '+str(row['commit_sha'])+' @ '+str(datetime.now().strftime("%H:%M:%S")))
		if index > start_from:
			process = subprocess.Popen('echo '+str(row['commit_sha'])+' | ~/lookup/getValues c2p', shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
			out, err = process.communicate()
			project_url_array = out.rstrip().split(';')[1:]
			if len(project_url_array) > 1:
				woc_commits.at[index, 'is_in_other_projects'] = 1
				woc_commits.at[index, 'number_of_other_projects_it_is_in'] = len(project_url_array) - 1
				woc_commits.at[index, 'urls_of_other_projects_it_is_in'] = project_url_array[1:]

			if index > start_from+2 and index % 1000 == 0:
				print('***** saving')
				woc_commits.to_csv('woc-commits.csv', sep=',', index=False, encoding='utf-8')

	woc_commits.to_csv('woc-commits.csv', sep=',', index=False, encoding='utf-8')

def getP2C(inputfile):
	woc_urls = pd.read_csv(inputfile, sep=',')

	df_columns = ['devpost_id', 'github_url', 'woc_url', 'commit_sha']
	woc_commits = pd.DataFrame(columns = df_columns)

	for index, row in woc_urls.iterrows():
		print('index: '+str(index)+' @ '+str(datetime.now().strftime("%H:%M:%S")))
		process = subprocess.Popen('echo '+str(row['woc_url'])+' | ~/lookup/getValues p2c', shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		out, err = process.communicate()
		commit_array = out.rstrip().split(';')
		if len(commit_array) > 1:
			commit_array = commit_array[1:]
			for commit_sha in commit_array:
				new_row = pd.Series([row['devpost_id'], row['woc_url'], row['hackathon_id'], commit_sha], index=df_columns)
				woc_commits = woc_commits.append(new_row, ignore_index=True)

	woc_commits.to_csv('woc-commits.csv', sep=',', index=False, encoding='utf-8')

def getB2C(directory):
	# old
	start_filename = 'burnt.csv'
	not_yet = False

	for filename in os.listdir(directory):
		if filename.endswith('.csv'):
			if filename == start_filename:
				not_yet = True
			else:
				if not not_yet:
					print('not yet '+str(filename))

			if not_yet:
				project_commits = pd.read_csv(directory+'/'+filename, sep=',')
				project_commits['commits_containing_blob'] = ''
				project_commits['number_of_commits_containing_blob'] = 0
				print('start '+str(filename+' '+str(len(project_commits.index))+' rows '+' @ '+str(datetime.now().strftime("%H:%M:%S"))))

				for index, row in project_commits.iterrows():
					process = subprocess.Popen('echo '+row['blob_sha']+' | ~/lookup/getValues b2c', shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
					out, err = process.communicate()
					number_of_commits_containing_blob = len(out.rstrip().split(';'))-1
					if number_of_commits_containing_blob > 100:
						project_commits.at[index, 'commits_containing_blob'] = 'TOOMANY'
					else:
						project_commits.at[index, 'commits_containing_blob'] = out.rstrip()
					project_commits.at[index, 'number_of_commits_containing_blob'] = len(out.rstrip().split(';'))-1

				project_commits.to_csv(directory+'/'+filename, sep=',', index=False, encoding='utf-8')
				print('end '+str(filename+' @ '+str(datetime.now().strftime("%H:%M:%S"))))
				print('*************************')

def createProjectCSVs():
	# old
	projects = pd.read_csv('woc-urls.csv', sep=',')
	commits = pd.read_csv('woc-commits.csv', sep=',')
	number_of_blobs = 0

	for index, row in projects.iterrows():
		print(str(index)+' start '+str(row['devpost_id']+' @ '+str(datetime.now().strftime("%H:%M:%S"))))
		selector = commits['devpost_id'] == row['devpost_id']
		project_commits = commits[selector]
		if len(project_commits.index) > 0:
			df_columns = ['commit_sha', 'commit_date', 'blob_sha']
			project_df = pd.DataFrame(columns = df_columns)
			print('blobs: '+str(project_commits['commit_size'].sum()))

			for project_commit_index, project_commit_row in project_commits.iterrows():
				if project_commit_row['tree_content'] == project_commit_row['tree_content']:
					tree_content = project_commit_row['tree_content'].split('##')
					for tree_item in tree_content:
						blob_sha = tree_item.split(';')[1]
						new_row = pd.Series([project_commit_row['commit_sha'], project_commit_row['commit_date'], blob_sha], index=df_columns)
						project_df = project_df.append(new_row, ignore_index=True)
						number_of_blobs = number_of_blobs + 1

			project_df.to_csv('projectCsvs/'+row['devpost_id']+'.csv', sep=',', index=False, encoding='utf-8')
		print('end '+str(row['devpost_id']+' @ '+str(datetime.now().strftime("%H:%M:%S"))))
		print('*************************')
	print('Number of Blobs: '+str(number_of_blobs))

if sys.argv[1] == 'p2c':
	getP2C('woc-urls.csv')
elif sys.argv[1] == 'c2p':
	getC2P('woc-commits.csv')
elif sys.argv[1] == 'commit_info':
	getCommitInformation('woc-commits.csv')
elif sys.argv[1] == 'commit_content':
	getCommitContent('woc-commits.csv')

#getB2C('projectCsvs')

#echo 05fe634ca4c8386349ac519f899145c75fff4169 | ~/lookup/getValues b2c (blob from commit)
#"Blob-ID";#ofCommits;"Commit-IDs"

#echo e4af89166a17785c1d741b8b1d5775f3223f510f | ~/lookup/getValues c2p (project from commit)
#"Commit-ID";#ofProjects;ProjectNames

#python grab_data.py p2c

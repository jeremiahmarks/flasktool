# What data do I have?

# Account.csv - Maps salesforce Account ID to a company name.
# Attachment.csv = Maps a file to a salesforce Account ID
# companyexport.csv - maps a company name to the first and last name of a contact, as well as the companyId (for easy searching)



# create a place to map salesforce AccountIDs to contactIds
salesforceAccountIdToInfusionsoftContactId={}
sfids=salesforceAccountIdToInfusionsoftContactId

# create a variable to hold the path to the file that the customer exported
###        ###
###  TO DO ###
###        ###
### make sure to add exported file to the main method as a global. 
exportedfile=''

def getmatchingrows(filename, columnname, value):
	"""This method will return a list of csv rows
	that have the matching value in the named
	column.
	"""
	matchingrows=[]
	with open(filename, 'rb') as infile:
		thisreader = csv.DictReader(infile)
		if columnname not in thisreader.fieldnames:
			print "Error, attempted to find value %s in column '%s' of file '%s'" %(value, columnname, filename)
		else:
			for eachrow in thisreader:
				if eachrow[columnname] == value:
					matchingrows.append(eachrow)
	return matchingrows

def pickACompanyrecord(listOfCompaniesWithSameName):
	"""This method exists in case there are multiple
	companies with the same name.  If there are, this
	method will pick first by existance of a primary
	contact, then, all other things being equal, 
	by the lowest ID
	"""
	bestmatch=listOfCompaniesWithSameName[0]
	firstnames = lambda rec1, rec2: rec1[''] and rec2
	lastnames = 
	for eachrecord in listOfCompaniesWithSameName:
		if eachrecord['Main Contact First Name'] and eachrecord['Main Contact Last Name']:
			if eachrecord['Id'] < bestmatch['Id']:
				bestmatch=eachrecord
			else:
				if not  bestmatch['Main Contact First Name'] and bestmatch['Main Contact Last Name']:
					bestmatch=eachrecord
					# Basically, how this works is:
						# since we are evaluating using 'and' this means that if there is anything in the value
						# it is true. If there is not (or it is literally False, but duck typing)
						# the expression will evaluate to false.
						#
						# So what we are saying is "If best match does not have both a first name and a last name
						# then this is already a superior contact because it does have both"
		elif bestmatch['Main Contact First Name'] and bestmatch['Main Contact Last Name']:
			# we know that the record has one or none of the fn/ln
			# that means that if the bestmatch has both, we are done
			pass
		# from here, we know that neither record has both names.
		# Basically, this should be:  
			# if either one has at least one value as well as a lower id, it is the best value.
		elif bestmatch['Main Contact First Name'] or bestmatch['Main Contact Last Name']:
			if bestmatch['Id']>eachrecord['Id']:
				bestmatch = eachrecord['Id']
	return bestmatch


def matchsfAccountIdtocontactid(salesforceaccountid, apiconnection):
	"""This method use the getmatchingrows method to 
	find the rows that match what they need to match.
	"""
	global exportedfile
	accountpath = os.path.join(basefolder, salesforceaccountfile)
	matchingSFAccounts = getmatchingrows(accountpath, 'Id', salesforceaccountid)
	if len(matchingSFAccounts)==0:
		return DEFAULT_CONTACT_TO_ATTACH_TO
	else:
		if len(matchingSFAccounts) > 1:
			print "There is an error. There appear to be multiple records with the id " + str(salesforceaccountid)
			return DEFAULT_CONTACT_TO_ATTACH_TO
		else:
			companyname = matchingSFAccounts[0]["Name"]
			matchingInfusionsoftcompanies = getmatchingrows(exportedfile, 'Company', companyname)
			if len(matchingInfusionsoftcompanies) == 0:
				return DEFAULT_CONTACT_TO_ATTACH_TO
			selectedCompanyRecord=pickACompanyrecord(matchingInfusionsoftcompanies)
			searchcriteria={}
			searchcriteria['CompanyID'] = selectedCompanyRecord['Id']
			if selectedCompanyRecord['Main Contact First Name']:
				searchcriteria['FirstName'] = selectedCompanyRecord['Main Contact First Name']
			if selectedCompanyRecord['Main Contact Last Name']:
				searchcriteria['LastName'] = selectedCompanyRecord['Main Contact Last Name']
			matchingcontacts=apiconnection.getallrecords('Contact', searchcriteria=searchcriteria, interestingdata=['Id'], orderedby='Id')
			print searchcriteria
			if len(matchingcontacts) == 0:
				return DEFAULT_CONTACT_TO_ATTACH_TO
			else:
				return matchingcontacts[0]






def attachfile(pathtofile, nameToUploadAs, contactIdToAttachTo, apiConnectionToUse):
	apiConnectionToUse.FileService.uploadFile(apiConnectionToUse.apikey, contactIdToAttachTo, nameToUploadAs, base64.b64encode(open(pathtofile, 'rUb').read()))




def processthefiles(basefolder, apiConnectionToUse):
	# The files should be structured as such:
	# - MainFolder
	# |--Files 
	# |--| This folder contains all of the files that are to be uploaded
	# |-Account.csv - the Account file from salesforce
	# |-Attachment.csv - this file is from salesforces export, too.
	# |-companyexport.csv - this is the full export of all fields from Infusionsoft
	"""This method will be the main logic operator
	thing.  
	"""
	with open(os.path.join(basefolder, attachmentExportFilename), 'rb') as infile:
		thisreader = csv.DictReader(infile)
		for eachrow in thisreader:
			currentFilename=eachrow['Id']
			realfilename=eachrow['Name']
			currentAccount = eachrow['AccountId']
			if currentAccount not in sfids.keys():
				# Basically, if it has not been mapped yet, we are going
				# to map it. Then, after everything else is done, we will
				# reference the value through the key.
				sfids[currentAccount] = matchsfAccountIdtocontactid(eachrow['AccountId'])
			attachfile(os.path.join(basefolder, "Files", currentFilename), realfilename, sfids[currentAccount], apiConnectionToUse)



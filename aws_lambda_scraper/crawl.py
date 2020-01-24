from bs4 import BeautifulSoup
#from urllib.request import Request, urlopen
#from urllib.error import HTTPError
import re

####### Function to check if a job role is a relevant internship ######
# takes in a string role and outputs bool if a role relates to comp sci majors
def relevant_internship(role):
	role = role.lower()
	#The logic that uses regex to see if role fits the bill
	regex_search_forward = re.search("(software|developer|engineering|(data science)|(machine learning)).*(intern|internship|co-op)", role)
	regex_search_backward = re.search("(intern|internship|co-op).*(software|developer|engineering|(data science)|(machine learning))", role)

	if ("internal" not in role) and (regex_search_forward or regex_search_backward):
		return True

	return False


####### CUSTOM SCRAPERS ###############################################################
def _flexport(driver):
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	results = []
	found = soup.find_all("div", {"class" : "flexRow _15wgy5e"})
	for x in found:
		role = x.find("a", {"class" : "_uxiekex"})
		#if re.search("(software|(data science)).*(intern|internship|co-op)", role.get_text().lower()) :
		if relevant_internship(role.get_text()):
			location = x.find_all("a", {"class" : "_1mhzlpgb"})[1].get_text()
			results.append((role.get_text(), location, "https://flexport.com"+role['href']))
	return results


def _akuna_capital(driver):
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	results = []
	found = soup.find_all("a", {"class" : "tmfw-single-job"})
	for x in found:
		role = x.find('h2').get_text()
		location = x.find('h4').get_text()
		href = "https://akunacapital.com" + x['href']
		results.append((role, location, href))
	return results


def _jane_street(driver):
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	results = []
	found = soup.find_all("div", {"class" : "position row"})
	for x in found:
		role = x.find("span", {"class" : "job-title"}).get_text()
		if role[-1] == ",":
			role = role[:-1]
		if relevant_internship(role):
			results.append((role, "US", "https://www.janestreet.com/join-jane-street/open-positions"))
	return results

def _lyft(driver):
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	results = []
	found = soup.find_all("a", {"class" : "_3-Uik_"})
	for x in found:
		role = x.find("div", {"class" : "_3mzA6h"}).get_text()
		if relevant_internship(role):
			link = x['href']
			location = x.find_all("div")[1].get_text()
			results.append((role, location, link))
	return results

def _rubrik(driver):
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	results = []
	base = soup.find_all("div", {"class" : "col-xs-12 office"})
	for x in base:
		location = x.find("span", {"class" : "office__name"}).get_text()
		jobs = x.find_all("div", {"class" : "job"})
		for job in jobs:
			role = job.find("p").get_text()
			if relevant_internship(role):
				link = "https://www.rubrik.com" + job.find("a")['href']
				results.append((role, location, link))
	return results

def _uber(driver):
	results = []
	try:
		# to load more results onto the page
		for _ in range(10):
			driver.find_element_by_xpath("//*[@class='ft nu qv lv qw be gw qx h2 ag fz qy']").click()
			driver.find_element_by_xpath("//*[@class='ft nu qv lv qw be gw qx h2 ag fz qy']").click()
			driver.find_element_by_xpath("//*[@class='ft nu qv lv qw be gw q h2 ag fz qy']").click()
	except:
		pass
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	found = soup.find_all("a", {"class" : "bg qr jh qs qt jm b5 mp mt"})
	for x in found:
		role = x.get_text()
		if relevant_internship(role):
			link = "https://www.uber.com" + x['href']
			location = "CA"
			results.append((role, location, link))
	return results


def _stripe(driver):
	results = []
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	found = soup.find_all("div", {"class" : "sc-bZQynM bCelqW"})
	for x in found:
		role = x.find("div", {"class" : "sc-bdVaJa hDQELU"}).get_text()
		if relevant_internship(role):
			link = "https://stripe.com" + x.find("a", {"class" : "common-Link sc-bwzfXH dPudUq"})['href']
			location = x.find("span", {"class" : " common-BodyText"}).get_text()
			results.append((role, location, link))
	return results


####### BATCH SCRAPERS ################################################################

# crawls a lever site and extracts any job openings which contain the word 'intern'
# return tuple of name, location, location
def _lever(driver):
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	results = []
	found = soup.find_all("a", {"class" : "posting-title"}, href=True)
	for x in found:
		commitment = x.find("span", {"class" : "sort-by-commitment posting-category small-category-label"}).get_text()
		location = x.find("span", {"class" : "sort-by-location posting-category small-category-label"}).get_text()
		role = x.find('h5').get_text()
		if relevant_internship(role):
			results.append((role, location, x['href']))
	return results


# Crawls a jobvite jobboard
def _jobvite(driver):
	results = []
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	found = soup.find_all("tr")
	for job_data in found:
		role = job_data.find("a", href=True).text
		if relevant_internship(role):
			link = ("https://jobs.jobvite.com/" +
					job_data.find("a", href=True)['href'])
			location = job_data.find("td", {"class":
											"jv-job-list-location"}).text
			# Removing white spaces and newlines from location
			location = ''.join(location.replace(" ", "").strip("\n").splitlines())
			results.append((role, location, link))

	return results

	## TODO -- add link to end of base url
def _greenhouse(driver, base_url):
	results = []
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	found = soup.find_all("section", {"class" : "level-0"})
	for x in found:
		# sometimes they're within h2 on greenhouse and sometimes h3
		section = (x.find("h2").get_text().lower() if x.find("h2") else x.find("h3").get_text().lower())
		if "engineering" in section or ("university" in section):
			#print(section)
			new_found = x.find_all("div", {"class" : "opening"})
			for y in new_found:
				role = y.find("a")
				#print(role.get_text())

				if relevant_internship(role.get_text()): #relevant_internship(role.get_text()):
					location = y.find("span", {"class" : "location"}).get_text()
					link = base_url + role['href']
					results.append((role.get_text(), location, link))

	return results

###  API ############################################################33

# applies func to a soup of site, to scrape it
def crawl_site(url, function, driver): #this needs to be modified a bit
	driver.get(url)
	results = []
	try:
		if function == "_greenhouse":
			return eval(function+"(driver,url)")
		else: #if function is _lever or something else
			return eval(function+"(driver)")  # may create a security vulnerability if db is compromised
	except:
		print("failed to open {}".format(url))
		return None #Changed this from [(0, 0, 0)]

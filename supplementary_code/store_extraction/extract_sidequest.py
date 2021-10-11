from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from utils import save_json, get_file_name, string_to_val, find_numeric_entries, format_key_string, normalize_text
import time
import json
import argparse
import os
import re

def check_dev_site(driver, index):
	block = driver.find_elements_by_css_selector("div.row.right-section.ng-star-inserted")[index]
	has_dev = False
	btns = block.find_elements_by_tag_name('sq-button')
	for btn in btns:
		if re.search("open website", btn.get_attribute("innerText").lower()):
			driver.execute_script("arguments[0].click();", btn)
			time.sleep(2)
			has_dev = True
			break

	if not has_dev:
		return None

	links = driver.find_elements_by_tag_name('a')
	url = None
	for l in links:
		if re.search("privacy policy", l.text.lower()):
			url = l.get_attribute('href')
			break

	return url

def get_oculus_policy(driver, btn):
	SIDEQUEST_LISTING = 0
	OCULUS_LISTING = 1
	POLICY_PAGE = 2

	driver.execute_script("arguments[0].click();", btn)
	driver.switch_to.window(driver.window_handles[OCULUS_LISTING])
	WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.app-description__title')))

	game_data = dict()
	if "oculus.com" not in driver.current_url:
		driver.close()
		driver.switch_to.window(driver.window_handles[SIDEQUEST_LISTING])
		time.sleep(2)
		return game_data

	try:	# check if game is on app lab = close pop up
		driver.find_element_by_css_selector("div.app-details__concept-app")
		ActionChains(driver).send_keys(Keys.ESCAPE).perform()
		game_data["Official_Oculus_Game"] = False
	except:	# if game is official (not app lab)
		game_data["Official_Oculus_Game"] = True

	# get privacy policy
	details = driver.find_element_by_class_name('app-details__header')
	driver.execute_script("arguments[0].scrollIntoView();",details)
	time.sleep(2)

	row_left = driver.find_elements_by_class_name("app-details-row__left")
	row_right = driver.find_elements_by_class_name("app-details-row__right")
	for index in range(len(row_left) - 1, 0, -1):
		left_name = row_left[index].get_attribute("innerText")
		if (left_name == "Developer Privacy Policy"):
			try:
				parent = row_right[index]
				link = parent.find_element_by_css_selector("a.app-details-row__link.link.link--clickable")
				link.click()	# this will open a new tab.
				driver.switch_to.window(driver.window_handles[POLICY_PAGE])

				time.sleep(2)
				game_data["Developer_Privacy_Policy"] = driver.current_url

				# close the new tab and switch to the previous tab
				driver.close()
				driver.switch_to.window(driver.window_handles[OCULUS_LISTING])
	
			except NoSuchElementException:
				game_data["Developer_Privacy_Policy"] = None

			break	# only interested in privacy policy link

	game_data["Oculus_url"] = re.split(r'\?', driver.current_url)[0]

	driver.close()
	driver.switch_to.window(driver.window_handles[SIDEQUEST_LISTING])
	time.sleep(2)
	return game_data

def display_all_games(driver):
	count = 0
	while True:
		items = driver.find_elements_by_css_selector("div.col.s12.relative.pointer.l3.m4.ng-star-inserted")
		if len(items) == count:
			break
		count = len(items)
		# driver.execute_script("arguments[0].scrollIntoView(true);", driver.find_elements_by_css_selector("div.footer-bottom")[-1])
		# time.sleep(1)
		driver.execute_script("arguments[0].scrollIntoView(true);", items[-1])
		time.sleep(3)

	return items

def get_game_data(driver, urls, output_dir):
	GROUP_SIZE = 3
	DOWNLOAD_HEADER = 'Downloads'
	SECTION_INDICIES = [4, 6, 7]
	FIRST_SECT_VALS = [0, 1, 3, -2]
	SECOND_SECT_VALS = [0, -5, -2]
	for url in urls:
		game_data = {}
		driver.get(url)
		time.sleep(3)
		# print(url)

		game_data["Sidequest_url"] = url
		game_data["App_Title"] = normalize_text(driver.find_element_by_css_selector("div.large-font").text)
		stats = driver.find_elements_by_css_selector("div.row.right-section.stats-padding")

		# popularity stats
		first_section = stats[SECTION_INDICIES[0]]
		first_section = re.split(r'[\n]+', normalize_text(first_section.text))

		game_data["Average_Rating"] = float(re.split(r'\/', first_section[FIRST_SECT_VALS[0]])[0])
		temp = re.split(r'[\s]+', first_section[FIRST_SECT_VALS[1]])[0]
		game_data["Review_Count"] = string_to_val(temp)
		game_data[DOWNLOAD_HEADER] = string_to_val(first_section[FIRST_SECT_VALS[2]])
		game_data[first_section[FIRST_SECT_VALS[3] + 1]] = string_to_val(first_section[FIRST_SECT_VALS[3]])

		# creator stats
		second_section = stats[SECTION_INDICIES[1]]
		second_section = re.split(r'[\n]+', normalize_text(second_section.text))

		game_data[second_section[SECOND_SECT_VALS[0] + 1]] = second_section[SECOND_SECT_VALS[0]]
		game_data[format_key_string(second_section[SECOND_SECT_VALS[1] + 1])] = string_to_val(second_section[SECOND_SECT_VALS[1]])
		game_data[format_key_string(second_section[SECOND_SECT_VALS[2] + 1])] = second_section[SECOND_SECT_VALS[2]]

		# timeline 
		third_section = stats[SECTION_INDICIES[2]]
		third_section = re.split(r'[\n]+', normalize_text(third_section.text))
		split_stats = [third_section[i:i+GROUP_SIZE] for i in range(0, len(third_section), GROUP_SIZE)]
		for stat in split_stats:
			value = stat[1]
			if re.search(r'[\d]', value):
				datetime_object = datetime.strptime(re.sub(',', '', value), '%b %d %Y')
				game_data[stat[-1]] = re.split(r'[\s]+', str(datetime_object))[0]
			else:
				game_data[stat[-1]] = value

		payment = driver.find_element_by_css_selector("div.right-section-padding-bottom.paid-title.right-section.row.ng-star-inserted").text
		game_data["Free"] = False if payment.find("Paid") != -1 else True

		try:
			game_data["Description"] = normalize_text(driver.find_element_by_css_selector("div.no-margin-bottom.right-section.row").text)
		except:
			game_data["Description"] = None

		btns = driver.find_element_by_css_selector("div.row.hide-on-large-only.center-align.top-buttons-margin").find_elements_by_tag_name('sq-button')
		store = None
		for btn in btns:
			if re.search(r'Download On Oculus', btn.get_attribute("innerText")):
				store = btn
				break

		blocks = driver.find_elements_by_css_selector("div.row.right-section.ng-star-inserted")
		tags, social = None, None
		for i, item in enumerate(blocks):
			if re.search(r'^(Search Tags)', item.get_attribute("innerText")):
				tags = i
			elif re.search(r'^(Social)', item.get_attribute("innerText")):
				social = i
				break

		game_data["Tags"] = [normalize_text(tag.get_attribute("innerText").strip()) for tag in blocks[tags].find_elements_by_tag_name("a")] if tags else []

		oculus_listing = False
		if store:
			res = get_oculus_policy(driver, store)
			if len(res) > 0: 
				oculus_listing = True
				for k, v in res.items():
					game_data[k] = v

		if (not store or not oculus_listing) and social:
			game_data["Developer_Privacy_Policy"] = check_dev_site(driver, social)

		if "Developer_Privacy_Policy" not in game_data:
			game_data["Developer_Privacy_Policy"] = None

		file_name = os.path.join(output_dir, get_file_name(game_data["App_Title"])) 
		# print(game_data)
		save_json(file_name, game_data)

def explore_store(driver, url, output_dir, links_only):
	driver.get(url)
	time.sleep(3)

	#only want games for oculus quest
	header = driver.find_element_by_css_selector("div.staff-picks-container")
	driver.execute_script("arguments[0].scrollIntoView(true);", header)
	time.sleep(3)

	filters = driver.find_elements_by_css_selector("sq-button.margin-right")
	driver.execute_script("arguments[0].click();", filters[-1])

	filters = driver.find_element_by_css_selector("div.filters.ng-star-inserted")
	filters = filters.find_elements_by_css_selector('div.col.s12.m3')
	options = filters[-1].find_elements_by_css_selector('div.col.s6')
	driver.execute_script("arguments[0].click();", options[0].find_elements_by_tag_name('li')[1].find_element_by_tag_name('a'))
	time.sleep(3)

	#get the links to all the game pages
	items = display_all_games(driver)
	links = [game.find_element_by_tag_name('a').get_attribute("href") for game in items]
	save_json("sidequest_links", links)

	if not links_only:
		get_game_data(driver, links, output_dir)

def main(path, output_dir, url_file, links_only):
	if not os.path.exists(path):
		print("ERROR: Invalid path for chrome driver given")
		return

	if url_file and not os.path.exists(url_file):
		print("ERROR: Invalid path for url file given")
		return

	if not os.path.exists(output_dir):
		os.mkdir(output_dir)

	options = webdriver.ChromeOptions()
	options.add_argument('--lang=en')	# set English as chromedriver's default language

	driver = webdriver.Chrome(executable_path = path, options=options)
	if not url_file:
		# extract urls from the website 
		explore_store(driver, "https://sidequestvr.com/apps/none/0/rating", output_dir, links_only)
	else:
		# already have list of game urls
		urls = json.load(open(url_file, "r"))
		get_game_data(driver, urls, output_dir)

	driver.quit()

if __name__ == "__main__":
	parser = argparse.ArgumentParser("Extract data from the SideQuest store")
	parser.add_argument("path", help = "Chrome driver path", type = str)
	parser.add_argument("output_dir", help = "Output directory", type = str)
	parser.add_argument("-url_file", help = "Path to url list file", type = str)
	parser.add_argument("--links_only", help = "Only create a url list file", action="store_true", default=False)

	args = parser.parse_args()
	main(args.path, args.output_dir, args.url_file, args.links_only)
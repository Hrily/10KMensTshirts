from bs4 import BeautifulSoup
import requests
import json
import csv
import time, datetime, sys, threading, subprocess

def get_datetime():
    return datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')

# Function to download images
# @param imgs List of image urls
def get_images(imgs):
    for img in imgs:
        subprocess.call('wget -q -P images "' + img + '"',  shell=True)

# Mens Tshirt URL
url = "http://www.jabong.com/men/clothing/polos-tshirts/?sort=popularity&dir=desc&limit=1000&page="
# Open csv file for writing
info_csv = open('info_' + get_datetime() + '.csv', 'w')
info_writer = csv.writer(info_csv, delimiter=',')
# Write headers
info_writer.writerow(['ID', 'Title', 'Original Price', 'Discount Price', 'Product URL', 'Product Image URL'])
info_writer.writerow([])
# Thread mutex for global resources
mutex = threading.Lock()
# Info List
info_list = []
# Image url List
img_urls = []

# Class for Fetch thread
class fetch_thread(threading.Thread):
    # Page to be fetched by this thread
    page = 0
    def __init__(self, p):
        super(fetch_thread, self).__init__()
        self.page = p
    
    def run(self):
        global url, mutex, info_list, proc_time, img_urls
        # Get contents of Page #page
        try:
            content = requests.get(url + str(self.page))
        except requests.exceptions.RequestException as e:
            # When failed to connect
            print "Exception"
            print e
            return
        # Cook soup of contents
        soup = BeautifulSoup(content.text, 'lxml')
        # Get all products
        shirts = soup.find_all('div', class_='product-tile')
        for shirt in shirts:
            # Skip dummy product
            if shirt.a['href'] == u'#':
                continue
            sid = shirt['data-product-id']
            title = shirt.find('div', class_='product-info').div.text
            prices = shirt.find_all('span', class_='standard-price')
            original_price = prices[0].string
            # If there is no discount
            discount_price = original_price
            # Else if there is a discount
            if len(prices) > 1:
                discount_price = shirt.find_all('span', class_='standard-price')[1].string
            surl = shirt.a['href']
            js = json.loads(shirt.img['data-img-config'])
            img_url = js['base_path'] + js['500']
            pos = shirt.a['data-pos']
            row = [pos, sid, title, original_price, discount_price, surl, img_url]
            # Append shirt info to info list
            # Also append image url to url list
            mutex.acquire()
            info_list.append(row)
            img_urls.append(img_url)
            mutex.release()
        print 'Wrote page ' + str(self.page)+ ' - ' + str(len(shirts)) + ' items'

# Start fetching pages
start_time = time.time()
threads = [ fetch_thread(i+1) for i in range(11) ]
[t.start() for t in threads]
[t.join() for t in threads]

# Sort shirts according to popularity
def getKey(item):
    return int(item[0])
info_list = sorted(info_list, key=getKey)

# Write to csv file
for row in info_list:
    info_writer.writerow([ unicode(s).encode("utf-8") for s in row[1:] ])
    info_csv.flush()

# Print details
exec_time = time.time() - start_time
exec_time = str(datetime.timedelta(seconds=exec_time))
print "\nTotal Execution time : "  + exec_time
# Close csv file
info_csv.close()

# Uncomment the following to download images
# get_images(img_urls)
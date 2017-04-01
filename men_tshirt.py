from bs4 import BeautifulSoup
import requests
import json
import csv
import time, datetime

def get_datetime():
    return datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')

# Function to download images
# @param imgs List of image urls
def get_images(imgs):
    for img in imgs:
        subprocess.call('wget -q -P images "' + img + '"',  shell=True)

# Mens Tshirt URL
url = "http://www.jabong.com/men/clothing/polos-tshirts/?sort=popularity&dir=desc&limit=2000&page="
# Open csv file for writing
info_csv = open('info_' + get_datetime() + '.csv', 'w')
info_writer = csv.writer(info_csv, delimiter=',')
# Write headers
info_writer.writerow(['ID', 'Title', 'Original Price', 'Discount Price', 'Product URL', 'Product Image URL'])
info_writer.writerow([])

items = 0                   # Items count
page = 1                    # Page count
proc_time = 0               # Processing time
img_urls = []               # Image url list
start_time = time.time()    # Start time
LIMIT = 10000               # Number of shirts to fetch

# Start geting items
while items < LIMIT:
    # Get contents of Page #page
    content = requests.get(url + str(page))
    proc_start_time = time.time()
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
        img_urls.append(img_url)
        # Write to csv
        row = [sid, title, original_price, discount_price, surl, img_url]
        info_writer.writerow([ unicode(s).encode("utf-8") for s in row ])
        info_csv.flush()
        items += 1
    proc_time += time.time() - proc_start_time
    print 'Wrote ' + str(items) + ' items in ' + str(datetime.timedelta(seconds=(time.time() - proc_start_time)))
    page += 1
exec_time = time.time() - start_time
exec_time = str(datetime.timedelta(seconds=exec_time))
print "\nTotal Execution time : "  + exec_time
proc_time = str(datetime.timedelta(seconds=proc_time))
print "Processing time : "  + proc_time
# Close csv file
info_csv.close()

# Uncomment the following to download images
# get_images(img_urls)
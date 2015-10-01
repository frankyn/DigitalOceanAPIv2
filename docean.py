#!/usr/bin/python
import dateutil.parser
from dateutil.relativedelta import *
import pytz
from datetime import *
import requests
import argparse
import os


# API_TOKEN
API_TOKEN=None

def account_request():
	# Request digital ocean droplets
	r = requests.get('http://api.digitalocean.com/v2/account',
					  auth=(API_TOKEN,""))
	
	# Get json
	information = r.json()
	return information

# Handle Account request
def account_handler():
	# Request Account information
	information = account_request()
	
	# format for display
	line_format = '{0:^15} {1:^30} {2:<60}'
	print(line_format.format('Droplet Limit','Email','UUID'))
	
	account = information['account']
	droplet_limit = account['droplet_limit']
	email = account['email']
	uuid = account['uuid']
	print(line_format.format(droplet_limit, email, uuid))

	# Process JSON and print status of servers
	# for droplet in information['droplets']:
	# 	droplet_id = droplet['id']
	# 	droplet_name = droplet['name']
	# 	droplet_ip = droplet['networks']['v4'][0]['ip_address']
	# 	print(droplet['created_at'])
	# 	print(line_format.format(droplet_id,droplet_name[:20],droplet_ip))

# Request droplet list
def request_droplets():
	# Request digital ocean droplets
	r = requests.get('http://api.digitalocean.com/v2/droplets',
					  auth=(API_TOKEN,""))
	
	# Get json
	information = r.json()
	return information

# Calculate running Cost
def calc_droplet_cost(monthly_cost, hourly_cost, created_at):
	# Get localized current time
	NOW = pytz.utc.localize(datetime.now())

	# Convert created_at
	droplet_created_at = dateutil.parser.parse(created_at)

	# Calculate Delta
	delta = relativedelta(NOW,droplet_created_at)

	# Calculate cost
	droplet_cost  = 12*monthly_cost*delta.years # 12 months per year
	droplet_cost += monthly_cost*delta.months 
	droplet_cost += 24*hourly_cost*delta.days # 24 hours per day
	droplet_cost += hourly_cost*delta.hours
	droplet_cost += (hourly_cost/60)*delta.minutes
	droplet_cost = round(droplet_cost,2)

	return droplet_cost

# Handle status request
def status_handler():
	# Request droplet list
	information = request_droplets()

	# Request sizes to calculate cost
	sizes = request_sizes()['sizes']
	# Generate a size index to call back into sizes object
	# This is ugly..
	size_index = [size['slug'] for size in sizes]

	
	# format for display
	line_format = '{0:^10} {1:^20} {2:<15} ${3:<10}'
	print(line_format.format('Id','Name','IP','Cost'))

	

	# Process JSON and print status of servers
	for droplet in information['droplets']:
		droplet_id = droplet['id']
		droplet_name = droplet['name']
		droplet_ip = droplet['networks']['v4'][0]['ip_address']
		droplet_size_index = size_index.index(droplet['size_slug'])

		droplet_monthly_cost = sizes[droplet_size_index]['price_monthly']
		droplet_hourly_cost = sizes[droplet_size_index]['price_hourly']
		droplet_created_at = droplet['created_at']
		
		droplet_cost = calc_droplet_cost(droplet_monthly_cost,
										 droplet_hourly_cost,
										 droplet_created_at)
		

		print(line_format.format(droplet_id,
								 droplet_name[:20],
								 droplet_ip,
								 droplet_cost))
				

# Request regions
def request_regions():
	# Request digital ocean regions
	r = requests.get('http://api.digitalocean.com/v2/regions',
					  auth=(API_TOKEN,""))
	
	# Get json
	information = r.json()

	return information

# Handle regions request
def regions_handler():
	information = request_regions()
	
	# format for display
	line_format = '{0:^10} {1:^20} {2:<45} {3:<30}'
	print(line_format.format('Slug','Name','Available Size Slugs','Features'))
	# Process JSON and print status of servers
	for region in information['regions']:
		# check if the region is available to us
		if region['available']:
			region_slug = region['slug']
			region_name = region['name']
			region_sizes = ','.join(region['sizes'])
			region_features = ','.join(region['features'])
			
			print(line_format.format(region_slug,region_name,
									 region_sizes,region_features))

# Request images 
def request_images():
	# Request digital ocean ssh keys
	r = requests.get('http://api.digitalocean.com/v2/images',
					  auth=(API_TOKEN,""))
	
	# Get json
	information = r.json()

	return information

# Handle Images List Request
def images_handler():
	# Request a list of images
	information = request_images()
	
	# format for display
	line_format = '{0:^10} {1:^15} {2:<15} {3:<55} {4:<10}'
	print(line_format.format('Id','Distribution','Name',
							 'Regions','Footprint'))

	# Process JSON and print status of servers
	for image in information['images']:
		image_id = image['id']
		image_name = image['name']
		image_type = image['type']
		image_distribution = image['distribution']
		image_regions = ','.join(image['regions'])
		image_min_disk_size = image['min_disk_size']
		
		print(line_format.format(image_id,image_distribution,
								 image_name,image_regions,
								 image_min_disk_size))

	
# Request SSH Key List
def request_keylist():
	# Request digital ocean ssh keys
	r = requests.get('http://api.digitalocean.com/v2/account/keys',
					  auth=(API_TOKEN,""))
	
	# Get json
	information = r.json()
	
	return information

# Handle SSH Key List request
def keylist_handler():
	# Get a list of keys
	information = request_keylist()
	
	# format for display
	line_format = '{0:^10} {1:^50} {2:<45}'
	print(line_format.format('Id','Fingerprint','Public_Key'))
	# Process JSON and print status of servers
	for key in information['ssh_keys']:
		key_id = key['id']
		key_fingerprint = key['fingerprint']
		key_public_keys = key['public_key'][-50:]
		
		print(line_format.format(key_id,key_fingerprint, key_public_keys))
	
# Request sizes list	
def request_sizes():
	# Request digital ocean ssh keys
	r = requests.get('http://api.digitalocean.com/v2/sizes',
					  auth=(API_TOKEN,""))
	
	# Get json
	information = r.json()
	
	return information

# Handle Size request
def sizes_handler():
	# Request sizes
	information = request_sizes()
	
	# format for display
	line_format = '{0:^10} ${1:<15} ${2:<15} {3:<10} {4:<10} {5:<10}'
	print(line_format.format('Slug','Price(M)','Price(H)',
							 'Memory','VCPUS','Disk','Regions'))

	# Process JSON and print status of servers
	for size in information['sizes']:
		# check if the size is available to us
		if size['available']:
			size_slug = size['slug']
			size_price_monthly = size['price_monthly']
			size_price_hourly = size['price_hourly']
			size_memory = size['memory']
			size_disk = size['disk']
			size_regions = ','.join(size['regions'])
	
			print(line_format.format(size_slug,size_price_monthly, 
									 size_price_hourly, size_memory,
									 size_disk, size_regions))
		

# Handle Create Handler
def create_handler(args):
	# Check if required arguments are filled.
	pass

# Load AUTH token
def load_token():
	global API_TOKEN
	
	which_script_path = os.path.dirname(__file__)
	which_script_path += '/.auth_token'
	
	try:
		with open(which_script_path,'r') as f:
			API_TOKEN = f.read()

	except:
		print 'Please enter your DigitalOcean auth token:'
		API_TOKEN = str(raw_input('->'))
		with open(which_script_path,'w+') as f:
			f.write(API_TOKEN)
	


# Request to delete droplet
def request_delete(droplet_id):
	# Request digital ocean droplets
	r = requests.delete(('http://api.digitalocean.com/v2/droplets/%s'%droplet_id),
					  auth=(API_TOKEN,""))
	# Get json
	if r.status_code == 204:
		print('Deleted droplet(%s)'%droplet_id)
	else:
		information = r.json()
		print(('\n\n%s'%information['message']))

# Handle Delete Droplet 
def delete_handler(args):
	# Get Droplet ID
	droplet_id = args.delete

	# Delete droplet
	request_delete(droplet_id)



if __name__ == "__main__":
	# load token
	load_token()
	# Process arguments
	parser = argparse.ArgumentParser(description='''
			Get important information from DigitalOcean API.
			''')
	
	# Account Information
	parser.add_argument("--account", const=True, default=False,
				action="store_const", dest="account",
				help="Request account information")

	# Status of Droplets
	parser.add_argument("--status", const=True, default=False, 
				action="store_const", dest="status",
				help="view status of all available droplets")

	# List Available Regions
	parser.add_argument("--regions", const=True, default=False,
				action="store_const", dest="regions", 
				help="view a list of available regions")

	# List of Available Images
	parser.add_argument("--images", const=True, default=False,
				action="store_const", dest="images",
				help="view a list of available images")


	# List Available SSH Keys
	parser.add_argument("--keylist", const=True, default=False,
				action="store_const", dest="keylist",
				help="view a list of available ssh keys")

	# List Available Sizes
	parser.add_argument("--sizes", const=True, default=False,
				action="store_const", dest="sizes",
				help="view a list of available sizes")


	# Droplet information
	parser.add_argument("--create", const=True, default=False, 
				action="store_const", dest="create",
				help="create a new droplet") 
	parser.add_argument("--name", type=str, default=None, dest="droplet_name",
				help="droplet name")
	parser.add_argument("--region", type=str, default=None, 
				dest="droplet_region", help="droplet region slug identifer")
	parser.add_argument("--size", type=str, default=None, dest="droplet_size",
				help="droplet size slug identifier")
	parser.add_argument("--image", type=str, default=None,dest="droplet_image",
				help="droplet image slug identifier")
	parser.add_argument("--sshkeys", type=list, default=None, 
				dest="droplet_sshkeys", help="droplet ssh keys")	


	# Droplet Delete
	parser.add_argument("--delete", type=str, default=False,
				dest="delete", help="delete a droplet by id")

	# Get results
	args = parser.parse_args()
	
	if args.account:
		account_handler()
	elif args.status:
		status_handler()
	elif args.regions:
		regions_handler()
	elif args.images:
		images_handler()
	elif args.sizes:
		sizes_handler()
	elif args.keylist:
		keylist_handler()
	elif args.create:
		create_handler(args)
	elif args.delete:
		delete_handler(args)
	

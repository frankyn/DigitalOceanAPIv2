#!/usr/bin/python
import dateutil.parser
from dateutil.relativedelta import *
import pytz
from datetime import *
import requests
import argparse
import os
import json

# hack for disabling warnings from requests module...
# Caused problems....
# requests.packages.urllib3.disable_warnings()

'''
	DigitalOcean V2 API Wrapper
'''
class DOcean:
	# constructor
	def __init__(self,api_token):
		self._api_token = api_token

	# Request Account Information
	def request_account(self):
		# Request digital ocean droplets
		r = requests.get('https://api.digitalocean.com/v2/account',
						  auth=(self._api_token,""))
		
		# Get json
		information = r.json()
		return information

	# Request Actions list
	def request_droplet_actions(self,droplet_id):
		# Request digital ocean droplets
		r = requests.get(('https://api.digitalocean.com/v2/droplets/%d/actions'%droplet_id),
						  auth=(self._api_token,""))
		
		# Get json
		information = r.json()
		return information

	# Request droplet list
	def request_droplets(self):
		# Request digital ocean droplets
		r = requests.get('https://api.digitalocean.com/v2/droplets',
						  auth=(self._api_token,""))
		
		# Get json
		information = r.json()
		return information

	# Calculate running Cost
	def calc_droplet_cost(self,monthly_cost, hourly_cost, created_at):
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

			
	# Request images 
	def request_images(self,private=False):
		# Request digital ocean ssh keys
		r = requests.get('https://api.digitalocean.com/v2/images?private='+str(private).lower(),
						  auth=(self._api_token,""))
		
		# Get json
		information = r.json()

		return information

	# Request regions
	def request_regions(self):
		# Request digital ocean regions
		r = requests.get('https://api.digitalocean.com/v2/regions',
						  auth=(self._api_token,""))
		
		# Get json
		information = r.json()

		return information
	

	# Request SSH Key List
	def request_keylist(self):
		# Request digital ocean ssh keys
		r = requests.get('https://api.digitalocean.com/v2/account/keys',
						  auth=(self._api_token,""))
		
		# Get json
		information = r.json()
		
		return information

	# Request sizes list	
	def request_sizes(self):
		# Request digital ocean ssh keys
		r = requests.get('https://api.digitalocean.com/v2/sizes',
						  auth=(self._api_token,""))
		
		# Get json
		information = r.json()
		
		return information

	
	# 
	# create a droplet
	def request_create(self,name, region, size, image, ssh_keys=[]):
		# headers 
		headers = {'Content-Type': 'application/json'}

		# payload
		payload = {
					"name": name,
					"region": region,
					"size": size,
					"image": image,
					"ssh_keys": ssh_keys
				  }

		
		# Request digital ocean ssh keys
		r = requests.post('https://api.digitalocean.com/v2/droplets',
						  auth=(self._api_token,""),
						  headers=headers,
						  data=json.dumps(payload))
		
		# Get json
		information = r.json()
		return (r.status_code,information)

	# Request to delete droplet
	def request_delete(self,droplet_id):
		# Request digital ocean droplets
		r = requests.delete(('https://api.digitalocean.com/v2/droplets/%s'%droplet_id),
						  auth=(self._api_token,""))
		# Get json
		if r.status_code == 204:
			print('Deleted droplet(%s)'%droplet_id)
		else:
			information = r.json()
			print(('\n\n%s'%information['message']))

	
'''
	Driver Class for DigitalOcean API wrapper
'''

class DOceanCLI:
	# Constructor 
	def __init__(self):
		# initialize auth_token
		self._auth_token = None

		# load token
		self.load_token()

		# Initialize DOcean API Wrapper
		self._docean = DOcean(self._auth_token)

		# Process arguments
		parser = argparse.ArgumentParser(description='''
			Get important information from DigitalOcean API.
		''')
		
		# Account Information
		parser.add_argument("--account", const=True, default=False,
					action="store_const", dest="account",
					help="Request account information")
		# Actions List
		parser.add_argument("--droplet_actions", default=False,
					type=int, dest="droplet_actions",
					help="Request droplet actions list")
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
		# List of Available Images
		parser.add_argument("--pimages", const=True, default=False,
					action="store_const", dest="pimages",
					help="view a list of private images")
		# List Available SSH Keys
		parser.add_argument("--keylist", const=True, default=False,
					action="store_const", dest="keylist",
					help="view a list of available ssh keys")
		# List Available Sizes
		parser.add_argument("--sizes", const=True, default=False,
					action="store_const", dest="sizes",
					help="view a list of available sizes")
		# Droplet information
		parser.add_argument("--create", default=None, nargs='+', 
					dest="create", 
					help="name region size image ssh_keys(optional)") 

		# Droplet Delete
		parser.add_argument("--delete", type=str, default=False,
					dest="delete", help="delete a droplet by id")

		# Get results
		args = parser.parse_args()
		
		if args.account:
			self.account_handler()
		elif args.droplet_actions:
			self.droplet_actions_handler(args)
		elif args.status:
			self.status_handler()
		elif args.regions:
			self.regions_handler()
		elif args.images:
			self.images_handler()
		elif args.pimages:
			self.private_images_handler()
		elif args.sizes:
			self.sizes_handler()
		elif args.keylist:
			self.keylist_handler()
		elif args.create:
			self.create_handler(args)
		elif args.delete:
			self.delete_handler(args)


	# Load AUTH token
	def load_token(self):
		which_script_path = os.path.dirname(__file__)
		which_script_path += '/.auth_token'
		
		try:
			with open(which_script_path,'r') as f:
				self._auth_token = f.read()

		except:
			print('Please enter your DigitalOcean auth token:')
			self._auth_token = str(raw_input('->'))
			with open(which_script_path,'w+') as f:
				f.write(self._api_token)

	# Handle Create Handler
	def create_handler(self,args):
		# Check if required arguments are filled.
		create_args = args.create
		droplet_name = None
		droplet_region = None
		droplet_size = None
		droplet_image = None
		droplet_sshkeys = []

		if len(create_args) < 4:
			print('Please provide all required arguments')
			return
		elif len(create_args) > 4:
			droplet_name = create_args[0]
			droplet_region = create_args[1]
			droplet_size = create_args[2]
			droplet_image = create_args[3]
			droplet_sshkeys = create_args[4].split(',')
		else:
			droplet_name = create_args[0]
			droplet_region = create_args[1]
			droplet_size = create_args[2]
			droplet_image = create_args[3]

		# Create a new droplet
		status,new_droplet = self._docean.request_create(droplet_name, 
									 droplet_region, 
									 droplet_size, droplet_image, 
									 droplet_sshkeys)

		# Check status
		if status == 202:
			droplet = new_droplet['droplet']
			print('Droplet %s (%d) was created'%(droplet_name,droplet['id']))

		else:
			print("Error creating a new droplet")

	
	# Handle regions request
	def regions_handler(self):
		information = self._docean.request_regions()
		
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


	# Handle Action Request
	def droplet_actions_handler(self,args):
		# Request Actions information
		information = self._docean.request_droplet_actions(args.droplet_actions)

		# Parse infromation
		actions_total = information['meta']['total']
		actions = information['actions']

		line_format = '{0:^15} {1:^20}'
		print(line_format.format('Type','Status'))
		for action in actions:
			print(line_format.format(action['type'],action['status']))


	# Handle status request
	def status_handler(self):
		# Request droplet list
		information = self._docean.request_droplets()

		# Request sizes to calculate cost
		sizes = self._docean.request_sizes()['sizes']
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
			
			droplet_cost = self._docean.calc_droplet_cost(droplet_monthly_cost,
											 droplet_hourly_cost,
											 droplet_created_at)
			

			print(line_format.format(droplet_id,
									 droplet_name[:20],
									 droplet_ip,
									 droplet_cost))
		

	# Handle Images List Request
	def private_images_handler(self):
		# Request a list of images
		information = self._docean.request_images(True)
		
		# format for display
		line_format = '{0:^10} {1:^15} {2:<15} {3:<15} {4:<55} {5:<10}'
		print(line_format.format('Id','Type','Distribution','Name',
								 'Regions','Footprint'))

		# Process JSON and print status of servers
		for image in information['images']:
			image_id = image['id']
			image_name = image['name']
			image_type = image['type']
			image_distribution = image['distribution']
			image_regions = ','.join(image['regions'])
			image_min_disk_size = image['min_disk_size']
			
			print(line_format.format(image_id,image_type,
									 image_distribution,
									 image_name,image_regions,
									 image_min_disk_size))

	# Handle Images List Request
	def images_handler(self):
		# Request a list of images
		information = self._docean.request_images()
		
		# format for display
		line_format = '{0:^10} {1:^15} {2:<15} {3:<15} {4:<55} {5:<10}'
		print(line_format.format('Id','Type','Distribution','Name',
								 'Regions','Footprint'))

		# Process JSON and print status of servers
		for image in information['images']:
			image_id = image['id']
			image_name = image['name']
			image_type = image['type']
			image_distribution = image['distribution']
			image_regions = ','.join(image['regions'])
			image_min_disk_size = image['min_disk_size']
			
			print(line_format.format(image_id,image_type,
									 image_distribution,
									 image_name,image_regions,
									 image_min_disk_size))

	# Handle SSH Key List request
	def keylist_handler(self):
		# Get a list of keys
		information = self._docean.request_keylist()
		
		# format for display
		line_format = '{0:^10} {1:^50} {2:<45}'
		print(line_format.format('Id','Fingerprint','Public_Key'))
		# Process JSON and print status of servers
		for key in information['ssh_keys']:
			key_id = key['id']
			key_fingerprint = key['fingerprint']
			key_public_keys = key['public_key'][-50:]
			
			print(line_format.format(key_id,key_fingerprint, key_public_keys))
	
	# Handle Size request
	def sizes_handler(self):
		# Request sizes
		information = self._docean.request_sizes()
		
		# format for display
		line_format = '{0:^10} ${1:<15} ${2:<15} {3:<10} {4:<10} {5:<10}'
		print(line_format.format('Slug','Price(M)','Price(H)',
								 'Memory','Disk','Regions'))

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
										 str(size_disk)+'GB', size_regions))
		

	# Handle Delete Droplet 
	def delete_handler(self,args):
		# Get Droplet ID
		droplet_id = args.delete

		# Delete droplet
		self._docean.request_delete(droplet_id)


	# Handle Account request
	def account_handler(self):
		# Request Account information
		information = self._docean.request_account()
		
		# format for display
		line_format = '{0:^15} {1:^30} {2:<60}'
		print(line_format.format('Droplet Limit','Email','UUID'))
		
		account = information['account']
		droplet_limit = account['droplet_limit']
		email = account['email']
		uuid = account['uuid']
		print(line_format.format(droplet_limit, email, uuid))


if __name__ == "__main__":
	# Initialize driver DOceanCLI
	doceancli = DOceanCLI()

	

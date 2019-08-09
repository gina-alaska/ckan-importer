#!/usr/bin/env python
import ckanapi
import json

site = ckanapi.RemoteCKAN(
    'http://ckan.url',
    apikey='...' # Found on CKAN user page.
)

voc_response = site.action.vocabulary_create(
    name='status'
)
print voc_response

# Read and create Status tags from status.json.
with open('status.json') as status_file:
    data = json.load(status_file)
    for tag in data['status']:
        response = site.action.tag_create(
            name=tag,
            vocabulary_id=voc_response['id']
        )
        print response

# Create a new Organization.
response = site.action.organization_create(
    name='example-organization',
    title='Example Organization'
)
print response

# Create a new Dataset.
response = site.action.package_create(
    title='Prudhoe Bay Map B',
    notes='Map B shapefile with all layers combined.',
    name='prudhoe_bay_map_b',
    status='Complete',                  # Dropdown
    archived_at='2019-08-06T05:39:42',  # Date
    request_contact_info='true',        # Boolean
    extras=[{                           # GeoJSON
        'key': 'spatial',
        'value': '{"type": "Polygon", "coordinates": [[[-162.0703125, 69.47296854140573], [-148.88671875, 69.47296854140573], [-148.88671875, 72.3424643905499], [-162.0703125, 72.3424643905499], [-162.0703125, 69.47296854140573]]]}'
    }],
    owner_org='example-organization'
)
print response

# Attach a URL as a resource to an existing Dataset.
response = site.action.resource_create(
     name='example-resource-url',
     package_id='prudhoe_bay_map_b',
     url='https://uaf.edu'
)
print response

# Upload a file resource to DataStore and attach it to an existing Dataset.
response = site.action.resource_create(
    name='example-resource-file',
    package_id='prudhoe_bay_map_b',
    upload=open('/Users/cstephenson/Downloads/UAFLogo_A_647.pdf', 'rb')
)
print response

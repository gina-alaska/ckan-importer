#!/usr/bin/env python
import ckanapi
import json

site = ckanapi.RemoteCKAN(
    'http://ckan.url',
    apikey='...' # Found on CKAN user page.
)

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
    status='Complete',
    archived_at='2019-08-06',
    iso_topic_category='001',
    extras=[{
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
     url='https://example.com'
)
print response

# Upload a file resource to DataStore and attach it to an existing Dataset.
response = site.action.resource_create(
    name='example-resource-file',
    package_id='prudhoe_bay_map_b',
    upload=open('/path/to/file', 'rb')
)
print response

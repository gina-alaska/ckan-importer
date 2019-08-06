#!/usr/bin/env python
import ckanapi

site = ckanapi.RemoteCKAN(
    'http://ckan.url',
    apikey='...' # Found on CKAN user page.
)

# Create a new Organization.
org = site.action.organization_create(
    name='example-organization',
    title='Example Organization'
)
print org

# Create a new Dataset.
pkg = site.action.package_create(
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
print pkg

# Attach a URL as a resource to an existing Dataset.
url_res = site.action.resource_create(
     name='example-resource-url',
     package_id='prudhoe_bay_map_b',
     url='http://example.com'
)
print url_res

# Upload a file resource to DataStore and attach it to an existing Dataset.
file_res = site.action.resource_create(
    name='example-resource-file',
    package_id='prudhoe_bay_map_b',
    upload=open('/path/to/file', 'rb')
)
print file_res

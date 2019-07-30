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
    name='example-dataset',
    title='Example Dataset',
    owner_org='example-organization'
)
print pkg

# Attach a URL as a resource to an existing Dataset.
url_res = site.action.resource_create(
     name='example-resource-url',
     package_id='example-dataset',
     url='http://example.com'
)
print url_res

# Upload a file resource to DataStore and attach it to an existing Dataset.
file_res = site.action.resource_create(
    name='example-resource-file',
    package_id='example-dataset',
    upload=open('/path/to/file', 'rb')
)
print file_res

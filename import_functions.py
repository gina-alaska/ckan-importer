# Functions for CKAN importer for Glynx JSON data
import datetime
import re

def create_organization(site, orgname):
    # Create a new Organization.
    response = site.action.organization_create(
        name=orgname,
        title=orgname,
        description='please change this',
        #image_url='https://path/to/image',
        #extras=[{
        #    'key': 'acronym',
        #    'value': 'EVERGREEN'
        #}]
    )
    return response

# Create a new Dataset.
def create_dataset(site, record, org):

    # Make sure that the slug will pass CKAN validation
    slug = record['slug']
    if slug == None:
        slug = record['title'].lower().replace(" ", "_")

    newslug = re.sub('[^a-zA-Z0-9 \-_\n\.]', '', slug)
    newslug = newslug.replace(".", "")
    record['slug'] = newslug[:100]
    print("**** " + newslug)

    # Make sure that the status is set to something
    if record['status'] == None:
        record['status'] = "Unknown"

    # Create the dataset
    response = site.action.package_create(
        title=record['title'],
        notes=record['description'],
        name=record['slug'],
        # maintainer='Example Maintainer',
        # maintainer_email='maintainer@example.com',
        status=record['status'],                  # Custom field with validator.
        # archived_at=record['archived_at'],      # Custom field with validator.
        archived_at=str(datetime.datetime.now()), # Custom field with validator.
        iso_topic_category='001',                 # Custom field with validator.
        extras=[{
            'key': 'spatial',               # Picked up by ckanext-spatial.
            'value': '{"type": "Polygon", "coordinates": [[[-162.0703125, 69.47296854140573], [-148.88671875, 69.47296854140573], [-148.88671875, 72.3424643905499], [-162.0703125, 72.3424643905499], [-162.0703125, 69.47296854140573]]]}'
        }],
        owner_org=org
    )
    print response

# Attach a URL as a resource to an existing Dataset.
def attach_url(data):
    response = site.action.resource_create(
         package_id='prudhoe_bay_map_b',
         name='Eskimo Walrus Commission',
         url='https://kawerak.org/natural-resources/eskimo-walrus-commission'
    )
    print response

# Upload a file resource to DataStore and attach it to an existing Dataset.
def attach_file(data):
    response = site.action.resource_create(
        package_id='prudhoe_bay_map_b',
        upload=open('/path/to/file', 'rb'),
        name='imported_locations'
    )
    print response

# This function deletes all of the datasets and organizations in the database so that the import can
# be ran without any conflicts with existing datasets.
def delete_all_datasets(site):
    datasets = site.action.package_list()
    for dataset in datasets:
        site.action.dataset_purge(id=dataset)

    orgs = site.action.organization_list()
    for org in orgs:
        site.action.organization_purge(id=org)

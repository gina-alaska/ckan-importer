# Functions for CKAN importer for Glynx JSON data
import datetime

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

    if record['slug'] == None:
        record['slug'] = 'slug-' + record['title'].lower().replace(" ", "_")

    if record['status'] == None:
        record['status'] = "Unknown"

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


# Functions for CKAN importer for Glynx JSON data
# import ckanapi

def create_organization(orgname):
    # Create a new Organization.
    response = site.action.organization_create(
        name=orgname,
        title='Change Me',
        description='Change Me',
        #image_url='https://path/to/image',
        #extras=[{
        #    'key': 'acronym',
        #    'value': 'EVERGREEN'
        #}]
    )
    print response

# Create a new Dataset.
def create_dataset(data):
    response = site.action.package_create(
        title='Prudhoe Bay Map B',
        notes='Map B shapefile with all layers combined.',
        name='prudhoe_bay_map_b',
        maintainer='Example Maintainer',
        maintainer_email='maintainer@example.com',
        status='Complete',                  # Custom field with validator.
        archived_at='2019-08-06',           # Custom field with validator.
        iso_topic_category='001',           # Custom field with validator.
        extras=[{
            'key': 'spatial',               # Picked up by ckanext-spatial.
            'value': '{"type": "Polygon", "coordinates": [[[-162.0703125, 69.47296854140573], [-148.88671875, 69.47296854140573], [-148.88671875, 72.3424643905499], [-162.0703125, 72.3424643905499], [-162.0703125, 69.47296854140573]]]}'
        }],
        owner_org='evergreen-state'
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


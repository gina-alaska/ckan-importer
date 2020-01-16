# Functions for CKAN importer for Glynx JSON data
import datetime
import re
import json
import geojson
import shapely.wkt, shapely.geometry

# ckanext-spatial does not support GeometryCollections.
# This function converts GeometryCollections into their corresponding
# single-part (Point, LineString, Polygon) or multi-part (MultiPoint,
# MultiLineString, or MultiPolygon) geometries.
def convert_geometrycollection(wkt):
    wkt_obj = shapely.wkt.loads(wkt)

    # Get all geom types inside GeometryCollection.
    geom_types = map(lambda x: x.geom_type, wkt_obj.geoms)

    # Tally all the types found in this GeometryCollection.
    # Homogenous GeometryCollections will only have one type to tally.
    tally = {}
    for type in geom_types:
        tally[type] = len(filter(lambda x: x == type, geom_types))

    # If there ever were a heterogenous GeometryCollection, the intention here
    # is to find what geometry type is used most often and make a new homogenous
    # geometry based on the most predominent geometry type. There does not
    # appear to be any heterogenous GeometryCollections in the Alaska EPSCoR
    # metadata, however, so this has only been tested against homogenous
    # GeometryCollections.
    predominant_type = max(tally, key=tally.get)

    # Pull geometries out of their GeometryCollection container in whatever
    # way is most appropriate.
    if predominant_type == 'Point':
        if tally['Point'] > 1:
            valid_wkt = shapely.geometry.MultiPoint(wkt_obj.geoms)
        else:
            valid_wkt = shapely.geometry.Point(wkt_obj.geoms[0])
    elif predominant_type == 'LineString':
        if tally['LineString'] > 1:
            valid_wkt = shapely.geometry.MultiLineString(wkt_obj.geoms)
        else:
            valid_wkt = shapely.geometry.LineString(wkt_obj.geoms[0])
    elif predominant_type == 'Polygon':
        if tally['Polygon'] > 1:
            valid_wkt = shapely.geometry.MultiPolygon(wkt_obj.geoms)
        else:
            valid_wkt = shapely.geometry.Polygon(wkt_obj.geoms[0])
    elif predominant_type in ['MultiPoint', 'MultiLineString', 'MultiPolygon']:
        valid_wkt = wkt_obj.geoms[0]

    # Return as a GeoJSON string.
    geom_json = geojson.Feature(geometry=valid_wkt, properties={})
    return json.dumps(geom_json['geometry'])

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
def create_dataset(site, record, org, archive):

    # Make sure that the slug will pass CKAN validation
    slug = record['slug']
    if slug == None:
        slug = record['title'].lower().replace(" ", "_")

    newslug = re.sub('[^a-zA-Z0-9 \-_\n\.]', '', slug)
    newslug = newslug.replace(".", "")
    record['slug'] = newslug[:100]
    maintainer = "None"
    maintainer_email = ""
    phone = ""
    print("**** importing " + newslug)

    # Make sure that the status is set to something
    if record['status'] == None:
        record['status'] = "Unknown"

    # Set bounds if available
    if record['bounds']:
        bounds_value = record['bounds'][0]['geom']
    else:
        bounds_value  = ""

    if 'primary_contact' in record and record['primary_contact'] != None:
        if 'name' in record['primary_contact']:
            maintainer = record['primary_contact']['name']

        if 'email' in record['primary_contact']:
            maintainer_email = record['primary_contact']['email']

        if 'phone' in record['primary_contact']:
            phone = record['primary_contact']['phone']

    # Create the dataset
    print("###### importing metadata")
    response = site.action.package_create(
        title=record['title'],
        notes=record['description'],
        name=record['slug'],
        # maintainer='Example Maintainer',
        # maintainer_email='maintainer@example.com',
        status=record['status'],                  # Custom field with validator.
        # archived_at=record['archived_at'],      # Custom field with validator.
        archived_at=archive,
        # archived_at=str(datetime.datetime.now().isoformat()), # Custom field with validator.
        iso_topic_category='001',                 # Custom field with validator.
        owner_org=org,
        maintainer = maintainer,
        maintainer_email = maintainer_email,
        extras = { 'key': "Maintainer Phone Num", 'value': phone }
        )

    # Process record links
    print("###### importing links")
    for link in record["links"]:
        if link == {}:
            continue
        attach_url(record['slug'], site, link, archive)

    # Process attachments
    print("###### importing attachments")
    for attachment in record["attachments"]:
        if attachment == {}:
            continue
        if attachment["file_name"] == "imported_locations":
            json_file = ""
            with open('export/files/' + record['slug'] + "/" + attachment["file_name"]) as file:
                json_file = file.read()
            # g1 = geojson.loads(json_file)
            # g2 = shapely.geometry.shape(g1)
            # print(g2.wkt)
            gjson = json.loads(json_file)

            response = site.action.package_patch(
                id=record['slug'],
                extras=[{
                    'key': 'spatial',
                    'value': json.dumps(gjson["features"][0]["geometry"])
                }]
            )
        else:
            attach_file(record['slug'], site, attachment)
            response = site.call_action('resource_create', attachment, files=files)

            # Create the default view
            site.action.resource_create_default_resource_views(resource=response)

# Attach a URL as a resource to an existing Dataset.
def attach_url(package_title, site, link, archive):
    response = site.action.resource_create(
         package_id=package_title,
         name=link["category"] + " - " + link["display_text"],
         url=link["url"],
         archived_at=archive
    )

# Upload a file resource to DataStore and attach it to an existing Dataset.
def attach_file(package_title, site, file):
    response = site.action.resource_create(
        package_id=package_title,
        upload=open('export/files/' + package_title + "/" + file["file_name"], 'rb'),
        name=file["description"],
        size=file["file_size"]
    )

    # Create the default view
    site.action.resource_create_default_resource_views(resource=response)

# This function deletes all of the datasets, organizations, and groups in the database so that the
# import can be ran without any conflicts with existing datasets.
def delete_all_datasets(site):
    datasets = site.action.package_list()
    for dataset in datasets:
        site.action.dataset_purge(id=dataset)

    orgs = site.action.organization_list()
    for org in orgs:
        site.action.organization_purge(id=org)

    groups = site.action.group_list()
    for group in groups:
        site.action.group_purge(id=group)

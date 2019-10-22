# Functions for CKAN importer for Glynx JSON data
import datetime
import re
import geojson
import json
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

    print tally

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

def create_organization(site, org_slug, org_title, org_desc):
    # Create a new Organization.
    response = site.action.organization_create(
        name=org_slug,
        title=org_title,
        description=org_desc,
        #image_url='https://path/to/image',
        #extras=[{
        #    'key': 'acronym',
        #    'value': 'EVERGREEN'
        #}]
    )
    return response

def create_collection(site, col_slug, col_title, col_desc):
    # Create a new Group (aka Collection).
    response = site.action.group_create(
        name=col_slug,
        title=col_title,
        description=col_desc
    )
    return response

# Create a new Dataset.
def create_dataset(site, record, org, archive):

    # Make sure that the slug will pass CKAN validation
    slug = record['slug']
    if slug == None:
        slug = record['title'].lower().replace(" ", "_")

    newslug = record['slug']
    newslug = re.sub("[^a-zA-Z0-9 \-_\n\.]", "", newslug)
    print("**** importing " + newslug)

    package = {
        'title': record['title'],
        'notes': record['description'],
        'name': newslug,
        'extras': []
    }

    if 'primary_contact' in record and record['primary_contact'] != None:
        package['maintainer'] = record['primary_contact']['name']
        package['maintainer_email'] = record['primary_contact']['email']

    if 'status' in record and record['status'] != None:
        package['extras'].append({
            'key': 'status',
            'value': record['status']
        })

    if 'start_date' in record and record['start_date'] != None:
        package['extras'].append({
            'key': 'start_date',
            'value': record['start_date']
        })

    if 'end_date' in record and record['end_date'] != None:
        package['extras'].append({
            'key': 'end_date',
            'value': record['end_date']
        })

    if 'iso_topics' in record and record['iso_topics'] != None:
        package['extras'].append({
            'key': 'iso_topics',
            'value': record['iso_topics']
        })

    if 'geo_keywords' in record and record['geo_keywords'] != None:
        package['extras'].append({
            'key': 'geo_keywords',
            'value': record['geo_keywords']
        })

    if 'record_type' in record and record['record_type'] != None:
        package['extras'].append({
            'key': 'record_type',
            'value': record['record_type']
        })

    if 'data_types' in record and record['data_types'] != None:
        package['extras'].append({
            'key': 'data_types',
            'value': record['data_types']
        })

    if 'tags' in record and len(record['tags']) > 0:
        package['tags'] = map(lambda x: {'name': re.sub('[^a-zA-Z0-9 \-_\n\.]', '', x)}, record['tags'])

    if 'wkt' in record and record['wkt'] != None:
        geojson = convert_geometrycollection(record['wkt'])
        package['extras'].append({
            'key': 'spatial',
            'value': geojson
        })

    if org != None:
        package['owner_org'] = org

    # Create the dataset
    print("###### importing metadata")
    site.call_action('package_create', package)

    # Process record links
    print("###### importing links")
    for link in record["links"]:
        if link == {}:
            continue
        attach_url(record['slug'], site, link, archive)

    # Process attachments
    print("###### importing attachments")
    for attachment in record["attachments"]:
        if attachment == {} or attachment['category'] == "Private Download":
            continue
        attach_file(record['slug'], site, attachment, archive)

# Attach a URL as a resource to an existing Dataset.
def attach_url(package_title, site, link, archive):
    response = site.action.resource_create(
         package_id=package_title,
         name=link["category"] + " - " + link["display_text"],
         url=link["url"],
         archived_at=archive
         # archived_at=str(datetime.datetime.now().isoformat()) # Custom field with validator.
    )

# Upload a file resource to DataStore and attach it to an existing Dataset.
def attach_file(package_title, site, file, archive):
    response = site.action.resource_create(
        package_id=package_title,
        upload=open('export/files/' + file["file_name"], 'rb'),
        name=file["description"],
        size=file["file_size"],
        archived_at=archive
    )

    # Create the default view
    site.action.resource_create_default_resource_views(resource=response)

# This function deletes all of the datasets, organizations, and groups in the
# database so that the import can be ran without any conflicts with existing
# datasets.
def delete_all(site):
    datasets = site.action.package_list()
    for dataset in datasets:
        site.action.dataset_purge(id=dataset)

    orgs = site.action.organization_list()
    for org in orgs:
        site.action.organization_purge(id=org)

    groups = site.action.group_list()
    for group in groups:
        site.action.group_purge(id=group)

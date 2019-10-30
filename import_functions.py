# Functions for CKAN importer for Glynx JSON data
import datetime
import re
import json

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
    print("**** importing " + newslug)

    # Make sure that the status is set to something
    if record['status'] == None:
        record['status'] = "Unknown"

    # Set bounds if available
    if record['bounds']:
        bounds_value = record['bounds'][0]['geom']
    else:
        bounds_value  = ""

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
        owner_org=org
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
            with open('export/files/' + attachment["file_name"]) as json_file:
                json_file = json.load(json_file)

            response = site.action.package_patch(
                record['slug'],
                extras=[{
                    'key': 'spatial',
                    'value': json_file
                }]
            )
        else:
            attach_file(record['slug'], site, attachment)

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
        upload=open('export/files/' + file["file_name"], 'rb'),
        name=file["description"],
        size=file["size"]
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

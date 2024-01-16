def get_uuid(source_uuid, tenant_name):
    with open('uuid_translation_matrix.json', 'r') as f:
        data = f.read()
        uuids = data.get(source_uuid)
        clone_uuid = uuids.get(tenant_name)
    return clone_uuid
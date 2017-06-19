import critiquebrainz.frontend.external.musicbrainz_db as mb
from mbdata.utils.models import get_entity_type_model, get_link_model
from sqlalchemy.orm import joinedload


def entity_relation_helper(db, target_type, source_type, source_entity_id):
    """Get information related to relationships between different entities.

    Args:
        db (Session object): Session object.
        target_type (str): Type of target entity.
        source_type (str): Type of source entity.
        source_entity_id (int): ID of the source entity.

    Returns:
        List of objects of relationships between entities.
    """
    source_model = get_entity_type_model(source_type)
    target_model = get_entity_type_model(target_type)
    relation = get_link_model(source_model, target_model)

    query = db.query(relation).\
        options(joinedload("link", innerjoin=True)).\
        options(joinedload("link.link_type", innerjoin=True))
    if relation.entity0.property.mapper.class_ == relation.entity1.property.mapper.class_:
        links = get_relationship_links(relation, query, "entity0", "entity1", target_model, source_entity_id)
        links.extend(get_relationship_links(relation, query, "entity1", "entity0", target_model, source_entity_id))
    else:
        if source_model == relation.entity0.property.mapper.class_:
            links = get_relationship_links(relation, query, "entity0", "entity1", target_model, source_entity_id)
        else:
            links = get_relationship_links(relation, query, "entity1", "entity0", target_model, source_entity_id)
    return links


def get_relationship_links(relation, query, source_attr, target_attr, target_model, source_entity_id):
    """Get relationship links between two entities.

    Args:
        relation (mbdata.model): Model relating the two entities.
        query (Session.query): Query object.
        source_attr (str): 'entity0' or 'entity1' based on which represents source model in relation table.
        target_attr (str): 'entity0' or 'entity1' based on which represents target model in relation table.
        target_model (mbdata.model): Model of the target entity.
        source_entity_id (int): ID of the source entity.

    Returns:
        List of objects of relationships between entities.
    """
    source_id_attr = source_attr + "_id"
    query = query.filter(getattr(relation, source_id_attr) == source_entity_id)
    query = query.options(joinedload(target_attr, innerjoin=True))
    return query.all()

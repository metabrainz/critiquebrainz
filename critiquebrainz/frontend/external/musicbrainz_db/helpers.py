from mbdata.utils.models import get_link_model
from mbdata.models import Tag
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from critiquebrainz.frontend.external.musicbrainz_db.utils import ENTITY_MODELS


def get_relationship_info(*, db, target_type, source_type, source_entity_ids, includes_data):
    """Get information related to relationships between different entities.

    Keep in mind that includes_data (dict) is altered to contain the relationship objects
    keyed by the source entity MBIDs.

    Args:
        db (Session object): Session object.
        target_type (str): Type of target entity.
        source_type (str): Type of source entity.
        source_entity_ids (list): IDs of the source entity.
        includes_data (dict): Dictionary containing includes data of entities.
   """
    source_model = ENTITY_MODELS[source_type]
    target_model = ENTITY_MODELS[target_type]
    relation = get_link_model(source_model, target_model)

    query = db.query(relation).\
        options(joinedload("link", innerjoin=True)).\
        options(joinedload("link.link_type", innerjoin=True))
    if relation.entity0.property.mapper.class_ == relation.entity1.property.mapper.class_:
        _relationship_link_helper(relation, query, "entity0", "entity1", target_type, source_entity_ids, includes_data)
        _relationship_link_helper(relation, query, "entity1", "entity0", target_type, source_entity_ids, includes_data)
    else:
        if source_model == relation.entity0.property.mapper.class_:
            _relationship_link_helper(relation, query, "entity0", "entity1", target_type, source_entity_ids, includes_data)
        else:
            _relationship_link_helper(relation, query, "entity1", "entity0", target_type, source_entity_ids, includes_data)


def _relationship_link_helper(relation, query, source_attr, target_attr, target_type, source_entity_ids, includes_data):
    """Get relationship links between two entities.

    Keep in mind that includes_data (dict) is altered to contain the relationship objects
    keyed by the source entity MBIDs.

    Args:
        relation (mbdata.model): Model relating the two entities.
        query (Session.query): Query object.
        source_attr (str): 'entity0' or 'entity1' based on which represents source model in relation table.
        target_attr (str): 'entity0' or 'entity1' based on which represents target model in relation table.
        target_type (str): Type of the target entity.
        source_entity_ids (list): IDs of the source entity.
        includes_data (dict): Dictionary containing the includes data of entities.
   """
    source_id_attr = source_attr + "_id"
    query = query.filter(getattr(relation, source_id_attr).in_(source_entity_ids))
    query = query.options(joinedload(target_attr, innerjoin=True))
    relation_type = target_type + "-rels"
    for link in query:
        includes_data[getattr(link, source_id_attr)].setdefault('relationship_objs', {}).\
            setdefault(relation_type, []).append(link)


def get_tags(*, db, entity_model, tag_model, entity_ids):
    """Get tags associated with entities.

    Args:
        db (Session object): Session object.
        entity_model (mbdata.models): Model of the entity.
        tag_model (mbdata.models): Tag of the model.
        entity_ids (list): IDs of the entity whose tags are to be fetched

    Returns:
        List of tuples containing the entity_ids and the list of associated tags.
    """
    tags = db.query(entity_model.id, func.array_agg(Tag.name)).\
        join(tag_model).\
        join(Tag).\
        filter(entity_model.id.in_(entity_ids)).\
        group_by(entity_model.id).\
        all()
    return tags

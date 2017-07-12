from mbdata.utils.models import get_entity_type_model, get_link_model
from sqlalchemy.orm import joinedload


def entity_relation_helper(db, target_type, source_type, source_entity_ids, includes_data):
    """Get information related to relationships between different entities.

    Args:
        db (Session object): Session object.
        target_type (str): Type of target entity.
        source_type (str): Type of source entity.
        source_entity_ids (list): IDs of the source entity.
        includes_data (dict): Dictionary containing includes data of entities.
   """
    source_model = get_entity_type_model(source_type)
    target_model = get_entity_type_model(target_type)
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

    Args:
        relation (mbdata.model): Model relating the two entities.
        query (Session.query): Query object.
        source_attr (str): 'entity0' or 'entity1' based on which represents source model in relation table.
        target_attr (str): 'entity0' or 'entity1' based on which represents target model in relation table.
        target_type (str): Type of the target entity.
        source_entity_ids (list): IDs of the source entity.
        includes_data (dict): Dictionary containing the includes data of entities.

    Note:
        includes_data (dict) is altered to contain the relationship objects
        keyed by the source entity mbids
    """
    source_id_attr = source_attr + "_id"
    query = query.filter(getattr(relation, source_id_attr).in_(source_entity_ids))
    query = query.options(joinedload(target_attr, innerjoin=True))
    relation_type = target_type + "-rels"
    for link in query:
        includes_data[getattr(link, source_id_attr)].setdefault('relationship_objs', {}).\
            setdefault(relation_type, []).append(link)

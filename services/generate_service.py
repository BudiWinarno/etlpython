from database import SessionLocal
from models.template_mapping import TemplateMapping

def get_mapping(template_id):

    db = SessionLocal()

    mappings = db.query(TemplateMapping)\
                 .filter_by(template_id=template_id)\
                 .all()

    mapping_dict = {}

    for m in mappings:

        mapping_dict[m.excel_header] = m.standard_header

    db.close()

    return mapping_dict
EVENT_TYPE_COMPANY_CREATED = 'company_created'
EVENT_TYPE_COMPANY_DELETED = 'company_deleted'
EVENT_TYPE_COMPANY_UPDATED = 'company_updated'
EVENT_TYPE_CONTACT_CREATED = 'contact_created'
EVENT_TYPE_CONTACT_DELETED = 'contact_deleted'
EVENT_TYPE_CONTACT_UPDATED = 'contact_updated'
EVENT_TYPE_DEAL_CREATED = 'deal_created'
EVENT_TYPE_DEAL_DELETED = 'deal_deleted'
EVENT_TYPE_DEAL_UPDATED = 'deal_updated'

MESSAGE_EVENT_TO_EVENT_TYPE = {
    'contact.creation': EVENT_TYPE_COMPANY_CREATED,
    'contact.deletion': EVENT_TYPE_COMPANY_DELETED,
    'contact.propertyChange': EVENT_TYPE_COMPANY_UPDATED,
    'company.creation': EVENT_TYPE_CONTACT_CREATED,
    'company.deletion': EVENT_TYPE_CONTACT_DELETED,
    'company.propertyChange': EVENT_TYPE_CONTACT_UPDATED,
    'deal.creation': EVENT_TYPE_DEAL_CREATED,
    'deal.deletion': EVENT_TYPE_DEAL_DELETED,
    'deal.propertyChange' EVENT_TYPE_DEAL_UPDATED,
}

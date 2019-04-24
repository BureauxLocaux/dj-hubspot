from collections import defaultdict
import logging

from django.conf import settings

from hubspot3.companies import CompaniesClient
from hubspot3.contacts import ContactsClient
from hubspot3.deals import DealsClient
from hubspot3.engagements import EngagementsClient
from hubspot3.error import HubspotBadRequest, HubspotServerError
from hubspot3.products import ProductsClient
from hubspot3.properties import PropertiesClient
from hubspot3.property_groups import PropertyGroupsClient

logger = logging.getLogger('vendors.dj_hubspot')


class HubspotClient:
    """
    Required settings:

    - HUBSPOT_API_KEY

    """
    POST_REQUEST_DELAY = 1  # in seconds

    def wait(self, delay=None):
        time.sleep(delay or self.POST_REQUEST_DELAY)

    _companies_client = None
    _contacts_client = None
    _deals_client = None
    _engagements_client = None
    _products_client = None
    _properties_client = None
    _property_groups_client = None

    _mappings = {
        'companies': defaultdict(

            # property names are at this level
            lambda: defaultdict(

                # property values are at this level
                lambda: defaultdict(

                    # company ids are at this level
                    lambda: []
                )
            )
        ),  # lets us do self._mappings['companies']['key']['value'].append(id) in one pass  # noqa
    }

    def _get_property_groups_client(self):
        if not self._property_groups_client:
            self._property_groups_client = PropertyGroupsClient(api_key=settings.HUBSPOT_API_KEY)
        return self._property_groups_client

    def _get_properties_client(self):
        if not self._properties_client:
            self._properties_client = PropertiesClient(api_key=settings.HUBSPOT_API_KEY)
        return self._properties_client

    def _get_products_client(self):
        if not self._products_client:
            self._products_client = ProductsClient(api_key=settings.HUBSPOT_API_KEY)
        return self._products_client

    def _get_companies_client(self):
        if not self._companies_client:
            self._companies_client = CompaniesClient(api_key=settings.HUBSPOT_API_KEY)
        return self._companies_client

    def _get_contacts_client(self):
        if not self._contacts_client:
            self._contacts_client = ContactsClient(api_key=settings.HUBSPOT_API_KEY)
        return self._contacts_client

    def _get_deals_client(self):
        if not self._deals_client:
            self._deals_client = DealsClient(api_key=settings.HUBSPOT_API_KEY)
        return self._deals_client

    def _get_engagements_client(self):
        if not self._engagements_client:
            self._engagements_client = EngagementsClient(api_key=settings.HUBSPOT_API_KEY)
        return self._engagements_client


    # Property-related methods

    def _get_properties_raw_data(self, force_fetch=False):
        pass

    def _get_property_id(self, prop_name, force_fetch=False):
        pass

    def create_property(self, object_type, code, label, description,
                        group_code, data_type, widget_type, options=None):
        """
        The `code` parameter should not contain dashes, only underscores.

        Legal values for `object_type` are:
        - `companies`
        - `contacts`
        - `products`

        Legal values for `data_type` are:
        - `bool`
        - `datetime`
        - `enumeration`
        - `number`
        - `string`

        Legal values for `widget_type` are:
        - `checkbox`
        - `currency`
        - `date`
        - `file`
        - `number`
        - `radio`
        - `select`
        - `text`
        - `textarea`

        """
        prop_client = self._get_properties_client()
        params = {
            'object_type': object_type,
            'code': code,
            'label': label,
            'description': description,
            'group_code': group_code,
            'data_type': data_type,
            'widget_type': widget_type,
        }
        if options:
            params.update({
                'extra_params': {
                    'options': options,
                }
        })
        elif widget_type == 'currency':
            params.update({
                'widget_type': 'number',
                'extra_params': {
                    'displayMode': 'current_value',
                    'showCurrencySymbol': True,
                }
            })

        prop_client.create(**params)

    def delete_property(self, object_type, code):
        prop_client = self._get_properties_client()
        return prop_client.delete(object_type, code)

    def delete_all_custom_properties(self, object_type):
        prop_client = self._get_properties_client()
        return prop_client.delete_all_custom(object_type)

    def create_property_group(self, object_type, code, label):
        """

        Legal values for `object_type` are:
        - `companies`
        - `contacts`
        - `products`

        The `code` parameter should not contain dashes, only underscores.

        """
        pg_client = self._get_property_groups_client()
        return pg_client.create(object_type, code, label)

    def delete_property_group(self, object_type, code):
        pg_client = self._get_property_groups_client()
        return pg_client.delete(object_type, code)

    def delete_all_custom_property_groups(self, object_type):
        prop_client = self._get_property_groups_client()
        return prop_client.delete_all_custom(object_type)


    # Product-related methods

    def get_product_data(self, product_id):
        pass

    def get_all_products(self):
        pass

    def create_product(self, name, description, price, custom_fields=None):
        prod_client = self._get_products_client()
        prod_data = {
            'name': name,
            'description': description,
            'price': float(price),
        }
        if custom_fields:
            prod_data.update(custom_fields)
        print(prod_data)

        return prod_client.create(data=prod_data)

    def delete_product(self, product_id):
        pass

    def delete_all_products(self):
        pass

    # Company-related methods

    def get_company_data(self, company_id):
        pass

    def get_all_companies(self, extra_props=None):
        comp_client = self._get_companies_client()
        return comp_client.get_all(extra_props=extra_props or [])

    def _get_companies_mapping(self, prop_name, force_reindex=False):
        if force_reindex or len(self._mappings['companies'][prop_name]) == 0:

            print("/!\\ Indexing Hubspot companies on '%s' property" % prop_name, end='')

            mapping = defaultdict(lambda: [])
            all_companies = self.get_all_companies(extra_props=[prop_name])
            for company in all_companies:
                company_id = company.get('id')
                prop_value = company.get(prop_name)
                if company_id and prop_value:
                    mapping[prop_value].append(company_id)

                    print(".", end='')

            print("Indexing completed /!\\")

            self._mappings['companies'][prop_name] = mapping
        return self._mappings['companies'][prop_name]

    def filter_companies(self, prop_name, prop_value):
        mapping = self._get_companies_mapping(prop_name)
        return mapping.get(prop_value, mapping.get(str(prop_value)))

    def get_company_id_by_property_value(self, prop_name, prop_value):
        try:
            return self.filter_companies(prop_name, prop_value)[0]
        except (TypeError, IndexError):
            return None

    def create_company(self, company_data, **options):
        payload = {
            'properties': [
                {
                    'name': name,
                    'value': value,
                }
                for name, value in company_data.items()
            ]
        }
        comp_client = self._get_companies_client()
        return comp_client.create(payload, **options)

    def create_company_note(self, company_id, note_body, **options):
        payload = {
           'engagement': {
                'type': 'NOTE',
            },
            'associations': {
                'companyIds': [company_id],
            },
            'metadata': {
                'body': note_body,
            }
        }
        note_client = self._get_engagements_client()
        return note_client.create(payload, **options)

    def delete_all_companies(self, having=None):
        comp_client = self._get_companies_client()

        # No filter, delete everything.
        if not having:
            return comp_client.delete_all()

        # Otherwise, we have to filter the list.
        # First, we make sure to fetch the properties we want to filter upon...
        all_companies = self.get_all_companies(extra_props=having.keys())

        # Then, we build the filtered list...
        companies_to_delete = [
            company
            for company in all_companies
            if all([
                company.get(key) == value
                for key, value in having.items()
            ])
        ]

        # And finally, we can delete _only_ those companies.
        for company in companies_to_delete:
            comp_client.delete(company['id'])


    # Contact-related methods

    def get_contact_data(self, contact_id):
        pass

    def create_contact(self, company_data):
        payload = {
            'properties': [
                {
                    'property': name,
                    'value': value,
                }
                for name, value in company_data.items()
            ]
        }
        cont_client = self._get_contacts_client()
        return cont_client.create(payload)

    def link_contact_to_company(self, contact_id, company_id):
        cont_client = self._get_contacts_client()
        return cont_client.link_contact_to_company(contact_id, company_id)

    def create_contact_note(self, contact_id, note_body):
        payload = {
           'engagement': {
                'type': 'NOTE',
            },
            'associations': {
                'contactIds': [contact_id],
            },
            'metadata': {
                'body': note_body,
            }
        }
        note_client = self._get_engagements_client()
        return note_client.create(payload)

    def delete_all_contacts(self, having=None):
        cont_client = self._get_contacts_client()

        # No filter, delete everything.
        if not having:
            return cont_client.delete_all()

        # Otherwise, we have to filter the list.
        # First, we make sure to fetch the properties we want to filter upon...
        all_contacts = cont_client.get_all(extra_props=having.keys())

        # Then, we build the filtered list...
        contacts_to_delete = [
            contact
            for contact in all_contacts
            if all([
                contact.get(key) == value
                for key, value in having.items()
            ])
        ]

        # And finally, we can delete _only_ those contacts.
        for contact in contacts_to_delete:
            cont_client.delete(contact['id'])


    # Deal-related methods

    def get_deal_data(self, deal_id):
        pass

    def create_deal(self, deal_data):
        pass

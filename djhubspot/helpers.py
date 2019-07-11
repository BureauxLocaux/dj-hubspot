import logging
from _decimal import InvalidOperation

from django.conf import settings
from django.utils.functional import cached_property

from djhubspot.utils import hubspot_timestamp_to_datetime
from hubspot3.associations import AssociationsClient
from hubspot3.companies import CompaniesClient
from hubspot3.contacts import ContactsClient
from hubspot3.deals import DealsClient
from hubspot3.error import HubspotNotFound
from hubspot3.globals import (
    OBJECT_TYPE_COMPANIES,
    OBJECT_TYPE_CONTACTS,
    OBJECT_TYPE_DEALS,
    OBJECT_TYPE_PRODUCTS,
)
from hubspot3.lines import LinesClient
from hubspot3.owners import OwnersClient
from hubspot3.pipelines import PipelinesClient
from hubspot3.products import ProductsClient
from hubspot3.properties import PropertiesClient
from money.currency import Currency
from money.money import Money

from . import constants


logger = logging.getLogger('vendors.dj_hubspot')


class HubspotAPIObject:

    api_object_content = None

    _associations_client = None
    _companies_client = None
    _contacts_client = None
    _deals_client = None
    _engagements_client = None
    _lines_client = None
    _owners_client = None
    _pipelines_client = None
    _products_client = None
    _properties_client = None
    _property_groups_client = None

    def __init__(self, hubspot_id, fetch=True, **kwargs):
        self.api_object_content = {}
        self.hubspot_id = hubspot_id
        if fetch:
            self.fetch()

    def fetch(self):
        """Fetch the api object content and put it into `api_object_content`."""
        logger.debug(
            f"Fetching Hubspot API object of type '{self.__class__}' "
            f"with id: {self.hubspot_id} ..."
        )
        try:
            self.api_object_content = self._fetch_api_object()
        except HubspotNotFound:
            raise ValueError(
                f"Unable to find a {self.__class__} with Hubspot ID: {self.hubspot_id}"
            )

    @classmethod
    def from_api_object_content(cls, hubspot_id, api_object_content):
        """Instantiate the api object from an API response payload.

        This is useful to prevent to avoid performing too many requests
        to the Hubspot API.

        """
        api_object = cls(hubspot_id, fetch=False)
        api_object.api_object_content = api_object_content
        return api_object

    def _fetch_api_object(self):
        """Perform a call to the API to fetch the API object."""
        raise NotImplementedError

    @property
    def properties(self):
        return self.api_object_content.get('properties', {})

    def _get_property_value(self, property_name):
        """Safely retrieve the 'value' of a property."""
        try:
            return self.properties[property_name]['value']
        except KeyError:
            return None

    def update(self, data):
        """Update the object on hubspot."""
        # FIXME: Could the code be shared between all helpers?
        raise NotImplementedError

    # hubspot3 clients
    # ------------------------------------------------------------------------------

    @property
    def associations_client(self):
        if not self._associations_client:
            self._associations_client = AssociationsClient(api_key=settings.HUBSPOT_API_KEY)
        return self._associations_client

    @property
    def companies_client(self):
        if not self._companies_client:
            self._companies_client = CompaniesClient(api_key=settings.HUBSPOT_API_KEY)
        return self._companies_client

    @property
    def contacts_client(self):
        if not self._contacts_client:
            self._contacts_client = ContactsClient(api_key=settings.HUBSPOT_API_KEY)
        return self._contacts_client

    @property
    def deals_client(self):
        if not self._deals_client:
            self._deals_client = DealsClient(api_key=settings.HUBSPOT_API_KEY)
        return self._deals_client

    @property
    def lines_client(self):
        if not self._lines_client:
            self._lines_client = LinesClient(api_key=settings.HUBSPOT_API_KEY)
        return self._lines_client

    @property
    def owners_client(self):
        if not self._owners_client:
            self._owners_client = OwnersClient(api_key=settings.HUBSPOT_API_KEY)
        return self._owners_client

    @property
    def pipelines_client(self):
        if not self._pipelines_client:
            self._pipelines_client = PipelinesClient(api_key=settings.HUBSPOT_API_KEY)
        return self._pipelines_client

    @property
    def products_client(self):
        if not self._products_client:
            self._products_client = ProductsClient(api_key=settings.HUBSPOT_API_KEY)
        return self._products_client

    @property
    def properties_client(self):
        if not self._properties_client:
            self._properties_client = PropertiesClient(api_key=settings.HUBSPOT_API_KEY)
        return self._properties_client


class Company(HubspotAPIObject):
    """Help to manipulate companies through the Hubspot API."""

    @property
    def name(self):
        """The name of the company."""
        return self._get_property_value('name')

    @property
    def website(self):
        """The website of the company."""
        # TODO: Resolve complete address?
        return self._get_property_value('website')

    @property
    def address(self):
        """The address of the company."""
        return self._get_property_value('address')

    @property
    def address2(self):
        """The address2 of the company."""
        return self._get_property_value('address2')

    @property
    def country(self):
        """The country of the company."""
        return self._get_property_value('country')

    @property
    def city(self):
        """The city of the company."""
        return self._get_property_value('city')

    @property
    def zip(self):
        """The zip code of the company."""
        return self._get_property_value('zip')

    @cached_property
    def parent_company(self):
        """
        Return the parent of the company if it has one.

        Returns
        -------
        Company or None
        """
        hs_parent_id = self._get_property_value('hs_parent_company_id')
        if hs_parent_id:
            return Company(hs_parent_id)
        return None

    @cached_property
    def contacts(self):
        """The contacts related to the company."""
        contacts_vids = self.associations_client.get_company_to_contacts(self.hubspot_id)

        contacts = []
        for vid in contacts_vids:
            contact = Contact(vid)
            contacts.append(contact)

        return contacts

    def _fetch_api_object(self):
        """Fetch the api object by using the companies client."""
        return self.companies_client.get(
            self.hubspot_id,
        )

    def update(self, data):
        """
        Update the deal on hubspot with the given `data`.

        Parameters
        ----------
        data: dict
        """
        # FIXME: check how API update errors are raised. Unify the errors raised between
        # FIXME: hubspot3 and djhubspot?
        logger.debug(f"Updating company with hubspot id: {self.hubspot_id} ...")
        logger.debug(f"New company data: {data}")
        self.companies_client.update(
            self.hubspot_id,
            data,
        )


class Contact(HubspotAPIObject):

    @property
    def associated_company_id(self):
        """The id of the company associated to the contact (if there is one)."""
        return self._get_property_value('associatedcompanyid')

    @property
    def last_name(self):
        """The last name of the contact."""
        return self._get_property_value('lastname')

    @property
    def first_name(self):
        """The first name of the contact."""
        return self._get_property_value('firstname')

    @property
    def email(self):
        """The email of the contact."""
        return self._get_property_value('email')

    @property
    def phone(self):
        """The phone number of the contact."""
        return self._get_property_value('phone')

    @property
    def phone_number_country_code(self):
        """
        The country code associated to the phone number of the contact.

        Returns
        -------
        str:
            The country code associated to the phone number of the contact.
            Ex: `'FR'`
        """
        return self._get_property_value('hs_calculated_phone_number_country_code')

    def _fetch_api_object(self):
        """
        Fetch the api object by using the contacts client.

        Notes: contacts are retrieved by using a `vid`, acronym for 'Visitor ID'.
        """
        return self.contacts_client.get_contact_by_id(self.hubspot_id)

    def update(self, data):
        pass


class Line(HubspotAPIObject):

    _properties = []

    def __init__(self, hubspot_id, fetch=True, extra_properties=None):
        if extra_properties:
            self._properties += extra_properties
        super().__init__(hubspot_id, fetch)

    @property
    def is_product(self):
        """
        Check if the Line item is of type 'PRODUCT'. This is done by checking the presence of a
        `hs_product_id` key under the `properties` dict.

        Here is an `api_object_content` for a line of type 'PRODUCT':

        ```
        {
            "objectType":"LINE_ITEM",
            "portalId":5799819,
            "objectId":129392745,
            "properties":{
                ...
                "hs_product_id": {
                    "versions":[{...}],
                    "value":"24349443",
                    "timestamp":1556183427995,
                    "source":"CRM_UI",
                    "sourceId":"john.doo@company.com"
                }
            },
            "isDeleted":false,
        }
        ```
        Notes that other properties could be included depending of the `extra_properties` given
        during the init method.

        Returns
        -------
        bool:
            True if the Line object is of type 'PRODUCT'.
        """
        try:
            self.api_object_content['properties']['hs_product_id']
        except KeyError:
            logger.debug("The line item object do not contains any 'hs_product_id'.")
            return False
        except TypeError:
            # For any reason, the `api_object_content` is `None`.
            logger.debug("Cannot check the type of the line item object.")
            logger.debug(self.api_object_content)
            return False
        else:
            return True

    def _fetch_api_object(self):
        """Fetch the api object by using the lines client."""
        return self.lines_client.get(
            self.hubspot_id,
            params=[('properties', property_name) for property_name in self._properties],
        )

    def update(self, data):
        pass


class Product(HubspotAPIObject):
    """Help to manipulate products through the Hubspot API."""

    _properties = ['name', 'price']
    _line_item_hubspot_id = None

    def __init__(
            self,
            hubspot_id=None,
            fetch=True,
            extra_properties=None,
            **kwargs
    ):
        if extra_properties:
            self._properties += extra_properties

        super().__init__(hubspot_id=hubspot_id, fetch=fetch, **kwargs)

    @property
    def name(self):
        return self._get_property_value('name')

    @property
    def price(self):
        """The price of the product."""
        price = self._get_property_value('price')
        currency_code = 'EUR'  # FIXME: Retrieve this dynamically.

        try:
            return Money(price, getattr(Currency, currency_code))
        except (InvalidOperation, KeyError, TypeError):
            return None

    @classmethod
    def from_line_item(cls, line_item):
        """
        Instantiate a `Product` from a `Line`. This is usefull to retrieve a
        product from the line items of a Deal.

        Parameters
        ----------
        line_item: Line

        Returns
        -------
        Product

        Raises
        ------
        ValueError:
            If the given `line_item` is not of type `PRODUCT`.

        """
        if not line_item.is_product:
            logger.error(
                "Cannot instantiate hubspot product from line_item.",
                exc_info=True,
                extra={
                    'api_object_content': line_item.api_object_content,
                }
            )
            # TODO: Raise a custom error?
            raise ValueError(
                "The given 'line_item' do not contains an 'hs_product_id' property, meaning that "
                "the item is not of type 'PRODUCT'."
            )

        api_object_content = line_item.api_object_content
        object_properties = api_object_content['properties']

        hs_product_id_dict = object_properties.pop('hs_product_id')
        product_id = hs_product_id_dict['value']

        # Create a product api object content from information of the line item.
        product_api_object_content = {
            'objectType': constants.OBJECT_TYPE_PRODUCT,
            'objectId': product_id,
            **api_object_content,
        }

        product = cls(hubspot_id=product_id, fetch=False)
        product.api_object_content = product_api_object_content
        return product

    def _fetch_api_object(self):
        return self.products_client.get_product_by_id(
            self.hubspot_id,
            params=[('properties', property_name) for property_name in self._properties],
        )

    def update(self, data):
        pass


class Owner(HubspotAPIObject):
    """Help to manipulate owners through the Hubspot API."""

    @property
    def first_name(self):
        """The first name of the owner."""
        return self.api_object_content['firstName']

    @property
    def last_name(self):
        """The last name of the owner."""
        return self.api_object_content['lastName']

    @property
    def email(self):
        """The email of the owner."""
        return self.api_object_content['email']

    @classmethod
    def from_owner_email(cls, owner_email):
        owners_client = OwnersClient(api_key=settings.HUBSPOT_API_KEY)
        hs_owner_data = owners_client.get_owner_by_email(owner_email)
        if not hs_owner_data:
            return None
        return cls.from_api_object_content(hs_owner_data['ownerId'], hs_owner_data)

    def _fetch_api_object(self):
        return self.owners_client.get_owner_by_id(self.hubspot_id)

    def update(self, data):
        pass


class Deal(HubspotAPIObject):
    """Help to manipulate deals through the Hubspot API."""

    _products = []

    @property
    def name(self):
        """The name of the deal."""
        return self._get_property_value('dealname')

    @property
    def deal_currency_code(self):
        return self._get_property_value('deal_currency_code')

    @property
    def amount(self):
        # FIXME: Check between 'amount' and 'amount_in_home_currency'.
        _amount = self._get_property_value('amount_in_home_currency')
        currency_code = self.deal_currency_code

        try:
            return Money(_amount, getattr(Currency, currency_code))
        # FIXME: Clean handled exceptions.
        except (KeyError, InvalidOperation, TypeError):
            return None

    @cached_property
    def contacts(self):
        try:
            contacts_vids = self.api_object_content['associations']['associatedVids']
        except KeyError:
            logger.error(
                'Cannot retrieve a contact visitor ids from the deal.',
                extra={
                    'hubspot_id': self.hubspot_id,
                    'api_object_content': self.api_object_content,
                }
            )
            return None

        contacts = []
        for contact_vid in contacts_vids:
            contact = Contact(contact_vid)
            contacts.append(contact)

        return contacts

    @cached_property
    def company(self):
        """Retrieve the company linked to the deal."""
        # FIXME: Not sure why it could be many companies associated to a same deal. At the moment,
        # FIXME: we only take the first one.
        try:
            company_id = self.api_object_content['associations']['associatedCompanyIds'][0]
        except (KeyError, IndexError):
            logger.error(
                'Cannot retrieve a company id from the deal.',
                extra={
                    'hubspot_id': self.hubspot_id,
                    'api_object_content': self.api_object_content,
                }
            )
            return None
        return Company(company_id)

    @cached_property
    def owner(self):
        owner_id = self._get_property_value('hubspot_owner_id')
        if not owner_id:
            return None
        return Owner(owner_id)

    @cached_property
    def _pipeline(self):
        """
        The pipeline related to the deal.

        This method will fetch the pipeline from the hubspot API. It cost one API call.

        Returns
        -------
        dict
        """
        # TODO: At the moment, we dont use any Pipeline helper. We'll see later if it could be
        # TODO: usefull.
        try:
            pipeline_id = self.api_object_content['properties']['pipeline']['value']
        except (KeyError, ValueError):
            # TODO: Something bad happen ... Find the best way to handle it.
            logger.error(
                "Cannot retrieve `pipeline_id` for Deal.",
                exc_info=True,
                extra={
                    'hubspot_id': self.hubspot_id,
                    'api_object_content': self.api_object_content,
                }
            )
            return None
        else:
            return self.pipelines_client.get_deals_pipeline_by_id(pipeline_id)

    @cached_property
    def deal_stage(self):
        """
        The current stage of the deal.

        Returns
        -------
        dict
            The deal stage as returned by the hubspot API.
            Ex:
            ```
            {
                'stageId': '63f9dc05-5bcb-4899-b9e4-504a2a04855d',
                'createdAt': 0,
                'updatedAt': 1556114319558,
                'label': 'Deal concluded',
                'displayOrder': 2,
                'metadata': {'isClosed': 'true', 'probability': '1.0'},
                'active': True
            }
            ```

            `None` could be returned if we encounter an issue while trying to read information
            from the API responses.
        """
        # TODO: At the moment, we dont use any DealStage helper. We'll see later if it could be
        # TODO: usefull.
        pipeline = self._pipeline
        if not pipeline:
            return None

        try:
            # We first retrieve the deal stage id from the properties of our deal.
            deal_stage_id = self.api_object_content['properties']['dealstage']['value']
        except (KeyError, ValueError):
            # TODO: Something bad happen ... Find the best way to handle it.
            logger.error(
                "Cannot retrieve `deal_stage_id` for Deal.",
                exc_info=True,
                extra={
                    'hubspot_id': self.hubspot_id,
                    'api_object_content': self.api_object_content,
                }
            )
            return None

        # We then retrieve all the stages for the pipeline associated to the deal ...
        stages = pipeline.get('stages', [])
        if not stages:
            logger.warning(
                "Pipeline for deal dont have any stage!",
                extra={
                    'hubspot_id': self.hubspot_id,
                    'api_object_content': self.api_object_content,
                    'pipeline_object_content': pipeline,
                }
            )

        # ... we looks in the pipeline for a deal stage matching the `deal_stage_id`
        deal_stage = None
        for stage in stages:
            if stage['stageId'] == deal_stage_id:
                deal_stage = stage
                break

        if not deal_stage:
            # This should not happen. At the moment we just log an error in order to be warned of
            # this issue.
            logger.error(
                "No stage is matching with the deal stage!",
                extra={
                    'hubspot_id': self.hubspot_id,
                    'api_object_content': self.api_object_content,
                    'pipeline_object_content': pipeline,
                    'deal_stage_id': deal_stage_id,
                }
            )

        return deal_stage

    @property
    def closed_won(self):
        """
        Define if the deal is closed won, meaning that it has been successfully concluded.

        In order to define if the deal is closed won, we read the `probability` metadata of the
        deal. This parameter define (from 0.0 to 1.0) the probability to conclude the deal.
        A value of '1.0' means that the deal has been concluded successfully.
        """
        try:
            probability = float(self.deal_stage['metadata']['probability'])
        except (KeyError, ValueError) as e:
            logger.error(
                "Cannot retrieve deal stage probability from deal.",
                exc_info=True,
                extra={
                    'hubspot_id': self.hubspot_id,
                    'deal_stage': self.deal_stage,
                    'exception': e,
                }
            )
            # FIXME: How should we handle this error?
            raise e
        else:
            return probability == 1

    @property
    def close_date(self):
        """When the deal has been closed (won or lost)."""
        close_date_timestamp = self._get_property_value('closedate')

        if not close_date_timestamp:
            return None

        return hubspot_timestamp_to_datetime(close_date_timestamp)

    @property
    def payment_mode(self):
        return self._get_property_value('payment_mode')

    # FIXME: Change to `cached_property`?

    # TODO: This cost few queries and should be explained. Also, the product-batch endpoint seems
    # TODO: not working at the moment ...
    @property
    def products(self, extra_properties=None):
        """
        Get the products associated to the deal.

        Products are associated to a deal as line items. This method will fetch products by using
        the `AssociationsClient` in order to retrieve the lines of type product associated to
        the deal.

        Notes
        -----
        This method will perform the following calls to the Hubspot API:
            - One call to the associations API.
            - A call per line item to the lines API.
        Lines are directly converted to product in order to avoid to perform an extra call to the
        product API.
        TODO: Is it safer to perform an extra call to products?
        """
        if self._products:
            # We already fetched the products API.
            return self._products

        logger.debug(f"Processing products for deal with hubspot_id: {self.hubspot_id} ...")

        products = []

        # We have to use the association client in order to retrieve the lines of type product
        # associated to our deal.

        properties_to_retrieve = [
            'name', 'price', 'quantity',
            'discount', 'hs_discount_percentage',
        ]
        if extra_properties:
            properties_to_retrieve.extend(extra_properties)

        lines_ids = self.associations_client.get_deal_to_lines_items(self.hubspot_id)
        for line_id in lines_ids:
            # We first retrieve the line by using the `LinesClient` ...
            line = Line(
                hubspot_id=line_id,
                # We explicitly ask for the name and for the price of the product.
                extra_properties=properties_to_retrieve,
            )
            # ... we then convert it into a product (if possible) ...
            try:
                product = Product.from_line_item(line)
            except ValueError:
                logger.warning(
                    "Cannot retrieve a product from the hubspot line object.",
                    extra={
                        'hubspot_id': line_id,
                        'api_object_content': line.api_object_content,
                    },
                )
            else:
                # ... we finally add the converted line item to the list of products.
                products.append(product)

        # The processing of the products is done. We now can safely save the products into the
        # deal.
        self._products = products

        logger.debug(
            f"Successfully processed products for deal with hubspot_id: {self.hubspot_id}."
        )

        return self._products

    def _fetch_api_object(self):
        """Fetch the deal from the API."""
        return self.deals_client.get(deal_id=self.hubspot_id)

    def update(self, data):
        """
        Update the deal on hubspot with the given `data`.

        Parameters
        ----------
        data: dict
        """
        # FIXME: check how API update errors are raised. Unify the errors raised between
        # FIXME: hubspot3 and djhubspot?
        logger.debug(f"Updating deal with hubspot id: {self.hubspot_id} ...")
        logger.debug(f"New deal data: {data}")
        self.deals_client.update(
            self.hubspot_id,
            data,
        )


class HubspotProperty:
    """
    Notes: `HubspotProperty` is currently not inheriting from `HubspotAPIObject` as it we dont currently don't support
    the fetching of an individual field.

    Fields dont have an id and should be fetched by their name:
    https://developers.hubspot.com/docs/methods/companies/get_company_property

    Property payload example:
    ```
    {
        "name":"current_contract_end_date",
        "label":"Date de fin de contrat",
        "description":"",
        "groupName":"customer_info",
        "type":"datetime",
        "fieldType":"date",
        "createdAt":1557317008241,
        "readOnlyDefinition":false,
        "updatedAt":1557317008241,
        "formField":false,
        "displayOrder":1,
        "readOnlyValue":false,
        "hidden":false,
        "mutableDefinitionNotDeletable":false,
        "favorited":false,
        "favoritedOrder":-1,
        "calculated":false,
        "externalOptions":false,
        "displayMode":"current_value",
        "showCurrencySymbol":null,
        "hubspotDefined":null,
        "createdUserId":null,
        "textDisplayHint":null,
        "numberDisplayHint":null,
        "optionsAreMutable":null,
        "referencedObjectType":null,
        "isCustomizedDefault":false,
        "searchableInGlobalSearch":false,
        "currencyPropertyName":null,
        "hasUniqueValue":false,
        "deleted":false,
        "updatedUserId":null,
        "options":[]
    }
    ```
    """

    api_object_content = None

    def __init__(self, api_object_content):
        self.api_object_content = api_object_content

    @property
    def name(self):
        return self.api_object_content['name']

    @property
    def type(self):
        return self.api_object_content['type']

    @property
    def field_type(self):
        return self.api_object_content['fieldType']

    @property
    def read_only(self):
        return self.api_object_content.get('readOnlyValue', False)


class HubspotProperties(HubspotAPIObject):
    """
    https://developers.hubspot.com/docs/methods/companies/get_company_properties
    """

    _properties = []

    def __init__(self, object_type, fetch=True, **kwargs):
        """
        Parameters
        ----------
        object_type: str
            The type of object for whom to fetch the properties.
            Should be one of `companies`, `contacts`, `deals`, `products`.
            The object type will be used as the hubspot id in order to fetch data from the API.
        """
        if object_type not in [
            OBJECT_TYPE_COMPANIES,
            OBJECT_TYPE_CONTACTS,
            OBJECT_TYPE_DEALS,
            OBJECT_TYPE_PRODUCTS,
        ]:
            raise ValueError(
                "The given object type: {} is not a valid properties type.".format(object_type)
            )
        super().__init__(hubspot_id=object_type, fetch=fetch, **kwargs)

    def _fetch_api_object(self):
        return self.properties_client.get_all(object_type=self.hubspot_id)

    @property
    def properties(self):
        """Retrieve properties as helper classes."""
        if not self._properties:
            for property_data in self.api_object_content:
                self._properties.append(HubspotProperty(property_data))

        return self._properties

    def update(self, data):
        raise NotImplementedError

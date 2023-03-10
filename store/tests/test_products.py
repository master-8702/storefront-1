import pytest
from model_bakery import baker
from rest_framework import status

from store.models import Collection, Product


@pytest.fixture
def create_product(api_client):
    def do_create_product(product):
        return api_client.post('/store/products/', product)

    return do_create_product


@pytest.mark.django_db
class TestCreateProduct:
    def test_if_user_is_admin_returns_201(self, authenticate, create_product):
        authenticate(is_staff=True)
        collection = baker.make(Collection)

        response = create_product({'title': 'a',
                                   'description': 'vb',
                                   'slug': 'a-b',
                                   'unit_price': 1,
                                   'inventory': 1,
                                   'collection': collection.id})

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_anonymous_returns_401(self, create_product):
        collection = baker.make(Collection)

        response = create_product({'title': 'a',
                                   'description': 'vb',
                                   'slug': 'a-b',
                                   'unit_price': 1,
                                   'inventory': 1,
                                   'collection': collection.id})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, create_product):
        authenticate(is_staff=False)
        collection = baker.make(Collection)

        response = create_product({'title': 'a',
                                   'description': 'vb',
                                   'slug': 'a-b',
                                   'unit_price': 1,
                                   'inventory': 1,
                                   'collection': collection.id})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, authenticate, create_product):
        authenticate(is_staff=True)

        response = create_product({'title': '',
                                   'description': '',
                                   'slug': '',
                                   'unit_price': '',
                                   'inventory': '',
                                   'collection': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRetrieveProduct:
    def test_if_product_exists_return_200(self, api_client):
        product = baker.make(Product)

        response = api_client.get(f'/store/products/{product.id}/')

        assert response.status_code == status.HTTP_200_OK

    def test_if_product_doesnt_exists_return_404(self, api_client):
        response = api_client.get('/store/products/9999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND



@pytest.mark.django_db
class TestUpdateProduct:
    def test_if_user_is_admin_data_is_valid_returns_200(self,api_client , authenticate):
        authenticate(is_staff=True)
        product = baker.make(Product)

        response = api_client.patch(f'/store/products/{product.id}/', {'title': 'changed_product_title'})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "changed_product_title"


    def test_if_user_is_authenticated_data_is_valid_returns_403(self,api_client , authenticate):
        authenticate()
        product = baker.make(Product)

        response = api_client.patch(f'/store/products/{product.id}/', {'title': 'changed_product_title'})

        assert response.status_code == status.HTTP_403_FORBIDDEN




@pytest.mark.django_db
class TestDeleteProduct:

    def test_if_user_is_admin_returns_204(self,api_client , authenticate):
        authenticate(is_staff=True)
        product = baker.make(Product)

        response = api_client.delete(f'/store/products/{product.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT


    def test_if_user_is_not_admin_returns_403(self,api_client , authenticate):
        authenticate()
        product = baker.make(Product)

        response = api_client.delete(f'/store/products/{product.id}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN
import pytest
import concurrent.futures
from app import chat_assistant

def test_get_product_info_existing():
    response = chat_assistant("Apple MacBook Pro").lower()
    assert all(value in response for value in [
        "16-inch", "16gb", "1tb ssd", "$2399"
    ])

def test_get_product_info_non_existing():
    response = chat_assistant("Alienware X17").lower()
    assert "not found" in response or "couldn't find" in response or "unavailable" in response or "is not currently available" in response or "is not available" in response or "not listed" in response

def test_get_product_stock_existing():
    response = chat_assistant("Check stock for Dell XPS 13").lower()
    assert "in stock" in response or "available" in response or "out of stock" in response

def test_get_product_stock_non_existing():
    response = chat_assistant("Check stock for Unknown Product").lower()
    assert "not found" in response or "couldn't find" in response or "unavailable" in response or "is not available" in response or "is not currently available" in response or "not listed" in response

def test_get_all_products():
    response = chat_assistant("Show all products").lower()
    assert "available products" in response or "here is a list of available products" in response

# def send_request():
#     """Simula una consulta al asistente"""
#     return chat_assistant("Apple MacBook Pro").lower()

# def test_assistant_scalability():
#     num_requests = 1 # Número de solicitudes simultáneas

#     with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
#         results = list(executor.map(lambda _: send_request(), range(num_requests)))

#     # Verificar que todas las respuestas contienen información esperada
#     for response in results:
#         assert "16-inch" in response
#         assert "16gb" in response
#         assert "1tb ssd" in response
#         assert "$2399" in response
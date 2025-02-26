import pytest
from app import chat_assistant

def test_get_product_info_existing():
    response = chat_assistant("Apple MacBook Pro").lower()
    assert "apple macbook pro" in response

def test_get_product_info_non_existing():
    response = chat_assistant("Alienware X17").lower()
    assert "not found" in response or "couldn't find" in response or "unavailable" in response

def test_get_product_stock_existing():
    response = chat_assistant("Check stock for Dell XPS 13").lower()
    assert "in stock" in response or "available" in response or "out of stock" in response

def test_get_product_stock_non_existing():
    response = chat_assistant("Check stock for Unknown Product").lower()
    assert "not found" in response or "couldn't find" in response or "unavailable" in response

def test_get_all_products():
    response = chat_assistant("Show all products").lower()
    assert "available products" in response or "here is a list of available products" in response

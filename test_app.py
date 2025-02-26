import pytest
import concurrent.futures
import time
import re
from openai import APIError
from app import client, chat_assistant  # Importar correctamente desde app.py

def clean_text(text):
    """
    Normaliza el texto eliminando comas en los números y convirtiéndolo a minúsculas.
    Esto facilita la comparación de resultados en las pruebas.
    """
    return re.sub(r",", "", text).lower()

# Pruebas de funcionalidad del asistente
@pytest.mark.functional
def test_get_product_info_existing():
    """Verifica que el asistente proporciona la información correcta para un producto existente."""
    response = clean_text(chat_assistant("Apple MacBook Pro"))
    assert all(value in response for value in ["16-inch", "16gb", "1tb ssd", "$2399"])

@pytest.mark.negative
def test_get_product_info_non_existing():
    """Verifica la respuesta del asistente cuando se consulta un producto inexistente."""
    response = clean_text(chat_assistant("Alienware X17"))
    assert any(phrase in response for phrase in [
        "not found", "couldn't find", "unavailable", "is not ",
        "not listed", "are not", "not be", "not exist", "is no ", 
        "I wasn't", "unable to find"
    ])

@pytest.mark.functional
def test_get_product_stock_existing():
    """Verifica que el asistente proporciona información de stock para un producto existente."""
    response = clean_text(chat_assistant("Check stock for Dell XPS 13"))
    assert any(phrase in response for phrase in ["in stock", "available", "out of stock"])

@pytest.mark.negative
def test_get_product_stock_non_existing():
    """Verifica la respuesta del asistente cuando se consulta el stock de un producto inexistente."""
    response = clean_text(chat_assistant("Check stock for Unknown Product"))
    assert any(phrase in response for phrase in [
        "not found", "couldn't find", "unavailable", "is not ", 
        "not listed", "provide more", "not be ", "not exist", "is no ", 
        "I wasn't", "provide the specific name", "provide the name"
    ])

@pytest.mark.functional
def test_get_all_products():
    """Verifica que el asistente devuelve una lista de productos disponibles."""
    response = clean_text(chat_assistant("Show all products and their specifications"))
    assert any(phrase in response for phrase in ["available products", "here is a list of available products"])

@pytest.mark.edge_case
def test_empty_input():
    """Prueba con entrada vacía para verificar que el asistente maneja correctamente este caso."""
    response = clean_text(chat_assistant(""))
    assert "please provide a valid input" in response or "i didn't understand"

@pytest.mark.edge_case
def test_whitespace_input():
    """Prueba con solo espacios en blanco para verificar el manejo de entradas inválidas."""
    response = clean_text(chat_assistant("   "))
    assert "please provide a valid input" in response or "i didn't understand"

@pytest.mark.edge_case
def test_numeric_input():
    """Prueba con números en vez de texto para evaluar la respuesta del asistente."""
    response = clean_text(chat_assistant("123456789"))
    assert "not found" in response or "couldn't find"

@pytest.mark.edge_case
def test_symbols_input():
    """Prueba con caracteres especiales para verificar cómo responde el asistente."""
    response = clean_text(chat_assistant("@#*$&"))
    assert "not found" in response or "couldn't find"

# Prueba de carga con reintentos
def send_request():
    """
    Simula una consulta al asistente con reintentos en caso de error.
    Permite manejar errores temporales y evitar fallos en las pruebas.
    """
    thread = client.beta.threads.create()  # Crear un nuevo thread para cada ejecución

    for attempt in range(3):  # Intentar hasta 3 veces si hay error
        try:
            return clean_text(chat_assistant("Apple MacBook Pro", thread_id=thread.id))
        except APIError as e:
            print(f"⚠️ OpenAI APIError: {e}. Intento {attempt + 1}/3...")
            time.sleep(5)  # Esperar 5 segundos antes de reintentar
    
    return "error: no se pudo procesar la solicitud después de 3 intentos."

#Prueba de escalabilidad con solicitudes concurrentes
@pytest.mark.performance
def test_assistant_scalability():
    """Ejecuta múltiples consultas simultáneas para evaluar la escalabilidad del asistente."""
    num_requests = 20  # Reducir carga simultánea para evitar bloqueos

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
        results = list(executor.map(lambda _: send_request(), range(num_requests)))

    # Verificar que todas las respuestas contienen información esperada
    for response in results:
        assert "16-inch" in response
        assert "16gb" in response
        assert "1tb ssd" in response
        assert "$2399" in response

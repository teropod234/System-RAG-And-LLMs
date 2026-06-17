import pandas as pd
import numpy as np
import os

def data_cleaning(data: pd.DataFrame) -> pd.DataFrame:
    """
    Función para limpiar y procesar los datos.
    """
    brands = [
        "microsoft", 
        "adobe", 
        "apple", 
        "hp", 
        "nvidia", 
        "intel", 
        "corsair", 
        "canon / nikon", 
        "sennheiser", 
        "bose", 
        "sony", 
        "oneplus", 
        "google", 
        "xiaomi", 
        "samsung", 
        "msi", 
        "dell", 
        "lenovo", 
        "asus"
    ]

    if data.empty:
        print("El DataFrame está vacío. No se puede limpiar.")
        return data
    
    data.dropna(inplace=True)  # Elimina filas con valores nulos
    data.drop_duplicates(inplace=True)  # Elimina filas duplicadas

    data['brand'] = np.random.choice(brands, size=len(data))

    data['brand'] = data['brand'].str.strip().str.title()  # Normaliza la columna 'brand'
    
    return data  # Devuelve el DataFrame limpio y procesado
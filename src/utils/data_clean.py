import pandas as pd
import numpy as np

FIRST_NAMES = [
    "Ana", "Luis", "María", "Carlos", "Elena", "Jorge", "Laura", "Pablo",
    "Sofía", "Miguel", "Lucía", "Diego", "Carmen", "Andrés", "Isabel", "Raúl",
    "Natalia", "Iván", "Claudia", "Héctor", "Patricia", "Óscar", "Rosa", "Marcos",
]

LAST_NAMES = [
    "García", "Martínez", "López", "Sánchez", "Pérez", "González", "Rodríguez",
    "Fernández", "Torres", "Ramírez", "Flores", "Vega", "Castro", "Ortega", "Molina",
]

POSITIVE_REVIEWS = [
    "Muy buena relación calidad-precio, lo recomiendo.",
    "Cumple lo que promete y llegó en buen estado.",
    "Excelente compra, volvería a elegirlo.",
    "Funciona perfectamente para uso diario.",
    "Superó mis expectativas, muy satisfecho.",
    "Buen rendimiento y acabados de calidad.",
    "Ideal para lo que necesitaba, totalmente recomendable.",
    "Sin problemas hasta ahora, muy contento con la compra.",
]

NEGATIVE_REVIEWS = [
    "No cumple del todo lo esperado, regular.",
    "Calidad mejorable para el precio que tiene.",
    "Tuve algunos problemas al principio.",
    "No lo recomendaría sin comparar otras opciones.",
    "Funciona, pero con limitaciones importantes.",
    "Esperaba más por el coste del producto.",
    "La experiencia de uso no ha sido la mejor.",
    "No repetiría la compra en este caso.",
]


def _add_review_columns(data: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    n = len(data)
    recommend_ratio = rng.uniform(0.90, 0.95)
    is_recommended = (rng.random(n) < recommend_ratio).astype(int)

    authors = [
        f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}" for _ in range(n)
    ]

    short_reviews = []
    for rec in is_recommended:
        pool = POSITIVE_REVIEWS if rec == 1 else NEGATIVE_REVIEWS
        short_reviews.append(rng.choice(pool))

    data["review_author"] = authors
    data["short_review"] = short_reviews
    data["is_recommended"] = is_recommended
    return data


def data_cleaning(data: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
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
        "asus",
    ]

    if data.empty:
        print("El DataFrame está vacío. No se puede limpiar.")
        return data

    data = data.copy()
    data.dropna(inplace=True)
    data.drop_duplicates(inplace=True)

    rng = np.random.default_rng(seed)
    data["brand"] = rng.choice(brands, size=len(data))
    data["brand"] = data["brand"].str.strip().str.title()

    data = _add_review_columns(data, rng)

    return data

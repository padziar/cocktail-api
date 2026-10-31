# Cocktail API

REST API do zarządzania koktajlami i ich składnikami, zbudowane w Django i Django REST Framework.

## Funkcjonalności

- Pełny CRUD dla składników i koktajli
- Koktajle z zagnieżdżonymi składnikami (ilość + jednostka) dzięki modelowi pośredniemu `CocktailIngredient`
- Paginacja (10 elementów na stronę, `?page=N`)
- Walidacja danych wejściowych (nazwy, niepowtarzające się składniki, dodatnie ilości)
- Filtrowanie, wyszukiwanie i sortowanie (django-filter)
- Testy automatyczne (`APITestCase`)
- Baza danych: domyślnie SQLite, PostgreSQL przez zmienną `DATABASE_URL`

## Uruchomienie (Windows PowerShell)

Wymagany Python 3.12 (lub 3.10+).

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Korzeń API: http://127.0.0.1:8000/api/
Panel admina: http://127.0.0.1:8000/admin/

### PostgreSQL (opcjonalnie)

Utwórz bazę danych i ustaw w pliku `.env`:

```
DATABASE_URL=postgres://USER:PASSWORD@localhost:5432/cocktails
```

Następnie ponownie uruchom `python manage.py migrate`.

## Endpointy

| Metoda | URL | Opis |
|---|---|---|
| GET, POST | `/api/ingredients/` | lista (z paginacją), tworzenie |
| GET, PUT, PATCH, DELETE | `/api/ingredients/{id}/` | szczegóły, edycja, usuwanie |
| GET, POST | `/api/cocktails/` | lista (z paginacją), tworzenie |
| GET, PUT, PATCH, DELETE | `/api/cocktails/{id}/` | szczegóły, edycja, usuwanie |

Próba usunięcia składnika użytego w koktajlu zwraca `409 Conflict`.

### Przykład: utworzenie koktajlu

```json
{
  "name": "Mojito",
  "category": "Long drink",
  "instructions": "Muddle mint with lime juice, add rum, top with soda.",
  "ingredients": [
    {"ingredient": 1, "amount": "50.00", "unit": "ml"},
    {"ingredient": 2, "amount": "10.00", "unit": "leaves"}
  ]
}
```

Dozwolone jednostki: `ml, cl, g, pcs, tsp, tbsp, dash, leaves`.

Uwaga: w przeglądarkowym interfejsie DRF użyj zakładki **Raw data** (JSON), bo formularz HTML nie obsługuje zagnieżdżonych list.

### Filtry

Koktajle: `name`, `category`, `is_alcoholic`, `ingredient` (nazwy rozdzielone przecinkami, koktajl musi zawierać wszystkie), `ingredient_id`, `search`, `ordering` (`name`, `category`, `created_at`).

Składniki: `name`, `is_alcoholic`, `search`, `ordering` (`name`, `id`).

Przykład, bezalkoholowe koktajle z miętą: `/api/cocktails/?is_alcoholic=false&ingredient=mint`

## Testy

```powershell
python manage.py test
```

## Możliwe usprawnienia

- Dokumentacja OpenAPI/Swagger (drf-spectacular)
- Użytkownicy, autoryzacja JWT, uprawnienia, autor koktajlu i recenzje
- Diagram schematu bazy danych
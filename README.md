# Cocktail API

REST API do zarządzania koktajlami i ich składnikami, zbudowane w Django i Django REST Framework.

## Funkcjonalności

- Pełny CRUD dla składników i koktajli
- Koktajle z zagnieżdżonymi składnikami (ilość + jednostka) dzięki modelowi pośredniemu `CocktailIngredient`
- Paginacja (10 elementów na stronę, `?page=N`)
- Walidacja danych wejściowych (nazwy, niepowtarzające się składniki, dodatnie ilości)
- Filtrowanie, wyszukiwanie i sortowanie (django-filter)
- Dokumentacja OpenAPI/Swagger: http://127.0.0.1:8000/api/docs/
- Testy automatyczne (`APITestCase`)
- Docker + PostgreSQL (lokalnie bez Dockera: SQLite)

## Schemat bazy danych

![Schemat bazy danych](docs/db-schema.png)

- `Ingredient` i `Cocktail` połączone relacją wiele-do-wielu przez tabelę `CocktailIngredient` (przechowuje ilość i jednostkę).
- Ten sam składnik nie może wystąpić dwa razy w jednym koktajlu (unikalna para `cocktail`, `ingredient`).
- Usunięcie koktajlu usuwa jego pozycje; składnika użytego w koktajlu nie da się usunąć (`409 Conflict`).

## Uruchomienie w Dockerze (zalecane, PostgreSQL)

Wymagany Docker Desktop.

```powershell
docker compose up --build
```

W drugim oknie terminala utwórz konto administratora:

```powershell
docker compose exec web python manage.py createsuperuser
```

- API: http://localhost:8000/api/
- Swagger: http://localhost:8000/api/docs/
- Panel admina: http://localhost:8000/admin/

Testy w kontenerze:

```powershell
docker compose exec web python manage.py test
```

Zatrzymanie: `docker compose down` (dane zostają), z usunięciem danych bazy: `docker compose down -v`.

## Uruchomienie lokalne (Windows PowerShell, SQLite)

Wymagany Python 3.12 (lub 3.10+).

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Aby użyć lokalnie PostgreSQL, ustaw w `.env`:

```
DATABASE_URL=postgres://USER:PASSWORD@localhost:5432/cocktails
```

## Endpointy

| Metoda | URL | Opis |
|---|---|---|
| GET, POST | `/api/ingredients/` | lista (z paginacją), tworzenie |
| GET, PUT, PATCH, DELETE | `/api/ingredients/{id}/` | szczegóły, edycja, usuwanie |
| GET, POST | `/api/cocktails/` | lista (z paginacją), tworzenie |
| GET, PUT, PATCH, DELETE | `/api/cocktails/{id}/` | szczegóły, edycja, usuwanie |

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

- Użytkownicy, autoryzacja JWT, uprawnienia, autor koktajlu i recenzje
- Ścisła walidacja wartości logicznych w filtrach
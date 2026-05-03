# Mango Guide

A refined Streamlit guide for collecting and browsing mango-led tasting notes around the world: fresh fruit, gelato, sorbet, desserts, drinks, savory dishes, and other mango-focused experiences.

## Features

- Supabase-backed review browser
- Editorial homepage summary
- Rankings page with filters and top tasting cards
- Folium world map for public, geocoded tasting places
- Password-protected admin area for review creation, editing, and deletion
- Image gallery from uploaded images or review image URLs
- Plotly stats by category, mango origin, reviewer, and score distribution
- Subtle Google Maps links without using the Google Maps API
- Local `.env` support and Streamlit secrets support for deployment

## Project Structure

```text
app.py
requirements.txt
README.md
assets/
  mango_varieties/
    alphonso.jpg
    kesar.jpg
    ataulfo.jpg
    kent.jpg
    keitt.jpg
    tommy-atkins.jpg
src/
  config.py
  db.py
  scoring.py
  charts.py
  ui.py
pages/
  0_Overview.py
  1_Rankings.py
  2_Map.py
  3_Add_Review.py
  4_Gallery.py
  5_Statistics.py
```

## Setup

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Create a `.env` file in the project root.

```env
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-anon-or-publishable-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
APP_PASSWORD=choose-a-review-entry-password
DEBUG=false
```

Use `SUPABASE_KEY` or `SUPABASE_ANON_KEY` for public read access. Add
`SUPABASE_SERVICE_ROLE_KEY` for admin write actions from Streamlit server-side
code. Never hardcode this key or expose it in browser-side code.

4. Create the Supabase table.

The database starts empty. Public pages show refined empty states until public
reviews are added from the password-protected admin page.

Review IDs are treated as strings in the app. In the current Supabase project
they are UUID values, and edit/delete actions preserve those UUID strings instead
of casting IDs to integers.

The app keeps tasting location and mango origin in the existing review fields:

- `city`: city where the tasting happened.
- `place_name`: optional address, shop, restaurant, gelateria, market, or home tasting label.
- `country`: optional mango origin, such as India, Pakistan, Mexico, Peru, Thailand, or Unknown.
- `latitude` and `longitude`: optional tasting-place coordinates used by the map.

```sql
create table if not exists public.reviews (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  name text,
  category text,
  country text,
  city text,
  place_name text,
  latitude double precision,
  longitude double precision,
  date_tasted date,
  reviewer text,
  price numeric,
  currency text,
  sweetness numeric,
  acidity numeric,
  aroma numeric,
  texture numeric,
  mango_intensity numeric,
  value_for_money numeric,
  final_score numeric,
  short_review text,
  image_url text,
  would_eat_again boolean default true,
  public boolean default true
);
```

If you created the table before half-point scoring was added, convert the score
columns from `integer` to `numeric`:

```sql
alter table public.reviews
  alter column sweetness type numeric using sweetness::numeric,
  alter column acidity type numeric using acidity::numeric,
  alter column aroma type numeric using aroma::numeric,
  alter column texture type numeric using texture::numeric,
  alter column mango_intensity type numeric using mango_intensity::numeric,
  alter column value_for_money type numeric using value_for_money::numeric,
  alter column final_score type numeric using final_score::numeric;
```

5. Run the app.

```powershell
streamlit run app.py
```

## Map and Coordinates

The Map page uses `folium`, `streamlit-folium`, and `geopy` to show an
editorial world map. It opens on the whole world with a clean CartoDB Positron
tile layer and uses score-aware circle markers.

Reviews are mapped in two ways:

- Manual coordinates, when both `latitude` and `longitude` are saved.
- Runtime address/city geocoding, when coordinates are missing but `place_name`
  and/or `city` are available.

Automatic placement uses Nominatim through `geopy`, requires no Google Maps API
key, and may be approximate. Manual coordinates are preferred for best accuracy.
The app caches geocoding results for display. The Map page also includes a
"Refresh missing coordinates" button that geocodes reviews with missing
coordinates and saves successful latitude/longitude results back to Supabase
with the service role key. Saved coordinates are preferred for Streamlit Cloud
and other deployments because they avoid repeated geocoding during page loads.
The refresh action only writes coordinates when both latitude and longitude are
currently missing; it does not overwrite manually entered coordinates.

To add coordinates manually:

1. Open the tasting place in Google Maps.
2. Right-click the point on the map.
3. Copy the latitude and longitude.
4. Paste them into the Add Review form.

The app also creates "Open in Google Maps" links for cards, map popups, and
mapped review lists. If coordinates exist, the link is generated as:

```text
https://www.google.com/maps/search/?api=1&query={latitude},{longitude}
```

If coordinates are missing, the link uses a normal encoded text search query
from Address / Place and/or City instead. No Google Maps API key is required,
no Google Maps API is integrated, and no billing-related dependency is needed.

## Supabase Storage for Images

The Add Review page supports direct browser uploads. Uploaded images are stored in the existing `reviews.image_url` field after one of these paths is created:

- A public Supabase Storage URL, when the `review-images` bucket is configured.
- A local `uploads/` path, used as a development fallback if Supabase Storage upload fails or is not available.

To configure Supabase Storage:

1. In Supabase, open Storage.
2. Create a bucket named `review-images`.
3. Make the bucket public, or add policies that allow public read access to objects in the bucket.
4. Ensure `SUPABASE_SERVICE_ROLE_KEY` is configured for trusted server-side uploads.

The app does not require additional environment variables for Storage. It reuses:

```env
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-anon-or-publishable-key
SUPABASE_ANON_KEY=optional-anon-key-fallback
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
APP_PASSWORD=choose-a-review-entry-password
```

The app expects RLS to allow public users to read only rows where `public = true`.
Anonymous inserts can stay disabled. Add, edit, delete, and image upload actions
use `SUPABASE_SERVICE_ROLE_KEY` after the admin enters `APP_PASSWORD`.

For local development fallback uploads, files are written to `uploads/`. That folder is ignored by git.

## Mango Variety Images

The Overview page includes a small editorial guide to mango varieties. Place local images in:

```text
assets/mango_varieties/
  alphonso.jpg
  kesar.jpg
  ataulfo.jpg
  kent.jpg
  keitt.jpg
  tommy-atkins.jpg
```

The app uses only these local files for the variety guide. If an image is missing, it renders a refined placeholder card with the variety name.

## Streamlit Deployment Secrets

In Streamlit Community Cloud or another hosted deployment, add these secrets instead of committing a `.env` file:

```toml
SUPABASE_URL = "your-project-url"
SUPABASE_KEY = "your-anon-or-publishable-key"
SUPABASE_ANON_KEY = "optional-anon-key-fallback"
SUPABASE_SERVICE_ROLE_KEY = "your-service-role-key"
APP_PASSWORD = "your-password"
```

Do not print or display `SUPABASE_SERVICE_ROLE_KEY` in the app. It should only
exist as an environment variable or Streamlit secret on the trusted server.
By default, the app hides technical tracebacks from the UI. Set `DEBUG=true`
only in trusted local development if you need full Streamlit error details.

## Scoring

If `final_score` is left empty in the Add Review form, the app calculates it from the category-specific scoring model in `src/scoring.py`.

Supported scoring categories:

- Fresh Mango
- Gelato
- Sorbet
- Dessert
- Drink
- Savory Dish
- Other

The database stores `acidity` as a raw 0-10 score. The app converts it internally into `acidity_balance`:

```text
acidity_balance = 10 - abs(acidity - 5) * 2
```

The result is clamped between 0 and 10. A raw acidity score around 5 is best, while too little or too much acidity is penalized.

Fresh Mango:

```text
final_score =
0.20 * sweetness +
0.15 * acidity_balance +
0.20 * aroma +
0.20 * texture +
0.15 * mango_intensity +
0.10 * value_for_money
```

Gelato, Sorbet, Dessert, Drink, Savory Dish, and Other:

```text
final_score =
0.15 * sweetness +
0.10 * acidity_balance +
0.15 * aroma +
0.20 * texture +
0.30 * mango_intensity +
0.10 * value_for_money
```

Scores are rounded to one decimal.

## Notes

- The app handles missing Supabase credentials with a warning instead of crashing.
- Empty tables show friendly empty states across pages.
- Public pages use the anon/publishable key and load only rows where `public = true`.
- Admin writes require `APP_PASSWORD` and `SUPABASE_SERVICE_ROLE_KEY`.
- Secrets are read from Streamlit secrets first, then environment variables.

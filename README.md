# Monitor de Política Internacional

Titulares de la Cancillería del Perú, economía global y conflictos armados, sin repetidos. Fuente: Google News RSS. Se actualiza solo cada 3 horas con GitHub Actions.

## Cómo publicarlo

1. Crea un repo en GitHub y sube esta carpeta:
   ```
   git init
   git add .
   git commit -m "Monitor de noticias"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
   git push -u origin main
   ```
2. En el repo: **Settings > Pages > Source: Deploy from a branch > main / (root)** y guarda.
3. Listo. La página queda en `https://TU_USUARIO.github.io/TU_REPO/` y el workflow la actualiza cada 3 horas (también puedes correrlo manual en la pestaña Actions).

## Ajustar temas

Edita los queries en `CATEGORIES` dentro de `fetch_news.py` y corre `python fetch_news.py` para probar.

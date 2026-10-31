# Asystent Radnego — Malbork (PWA)

Bezpłatna instalowalna wyszukiwarka interpelacji, odpowiedzi Burmistrza, głosowań imiennych i audytu uchwał Rady Miasta Malborka.

- **Wersja danych:** `version.json` (obecnie `1.60.0`)
- **Aplikacja:** `index.html` — PWA na GitHub Pages (telefon/komputer)
- **Wyszukiwarka z danymi:** `data/katalog-v1.60.0.html.gz` — wersjonowany pakiet HTML, zawierający zaindeksowaną bazę do wyszukiwania
- **Baza do pobrania:** `data/katalog-operacyjny-v1.60.0.sqlite.gz` — samodzielny SQLite z rejestrami operacyjnymi, relacjami oraz audytem uchwał
- **Tryb offline:** `sw.js`, który przechowuje ostatnią zainstalowaną wersję aplikacji
- **Kontrola integralności:** SHA-256 w `version.json`, sprawdzany przez przeglądarkę przed uruchomieniem danych.

## Instalacja na Androidzie

Otwórz stronę GitHub Pages w Chrome. Wybierz **Zainstaluj** lub **⋮ → Dodaj do ekranu głównego**. Uruchomienie z ikony otwiera tę samą aplikację, która może działać offline po pierwszym wczytaniu.

## Aktualizacje

Po publikacji nowszego `version.json` aplikacja wykrywa zmianę przy ponownym uruchomieniu, odzyskaniu połączenia, powrocie na ekran lub przez przycisk **Odśwież**. Wówczas pokazuje **Nowa wersja!**. Kliknięcie pobiera nowy pakiet, sprawdza sumę kontrolną i otwiera nową bazę.

Ważne: uaktualnienie baz w Bibliotece ChatGPT **nie aktualizuje automatycznie** GitHub Pages. Nowe, zweryfikowane dane muszą zostać opublikowane w tym repozytorium (nowy plik `.gz`, `version.json` i `sw.js`). To osobny etap synchronizacji.

## Publikowanie kolejnej wersji

1. Wygeneruj aktualną samodzielną stronę HTML z indeksu SQLite.
2. Skompresuj jako `data/katalog-vX.Y.Z.html.gz` (gzip) oraz aktualizuj `data/katalog-operacyjny-vX.Y.Z.sqlite.gz`.
3. W `version.json` zmień wersję, nazwy plików, datę publikacji i sumy SHA-256.
4. Zmień numer cache i listę zasobów w `sw.js`.
5. `git add . && git commit -m "Aktualizacja danych X.Y.Z" && git push` — GitHub Pages wdraża aktualizację.
6. Sprawdź adres HTTPS i przycisk **Odśwież** na telefonie.

## Granice odpowiedzialności

Program wskazuje relacje i możliwe sprzeczności; nie zastępuje opinii radcy prawnego, rozstrzygnięć wojewody ani RIO. Przynależność do komitetu wyborczego nie oznacza automatycznie członkostwa w koalicji. Dokumenty pochodzą z materiałów projektu; pełne teksty nie są dostępne dla każdej uchwały. Artykułowanie podobieństwa tematycznego nie jest dowodem sprzeczności.

W repozytorium nie należy publikować niezweryfikowanych danych osobowych, poufnych wiadomości ani całych nieprzejrzanych materiałów źródłowych.
